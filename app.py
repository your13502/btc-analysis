
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 自動每5分鐘刷新
st_autorefresh(interval=5 * 60 * 1000, limit=None, key="autorefresh")

st.set_page_config(page_title="BTC、黃金ETF 與高相關美股分析", layout="wide")

st.title("📊 BTC、黃金ETF(GLD) 與高相關美股走勢 + 相關性分析")

assets = {
    "BTC-USD": "Bitcoin",
    "COIN": "Coinbase",
    "MSTR": "MicroStrategy",
    "GLD": "Gold ETF (GLD)"
}

st.markdown("資料來源：Yahoo Finance | 期間：過去 180 天")

# 設定日期範圍
end_date = datetime.today()
start_date = end_date - timedelta(days=180)

# 顯示資料抓取的時間
fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 抓資料
data = {}
for symbol in assets:
    ticker = yf.Ticker(symbol)
    try:
        hist = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        if hist.empty or hist["Close"].dropna().empty:
            st.warning(f"⚠️ {assets[symbol]} 的資料無法抓取，請稍後再試。")
        else:
            data[symbol] = hist["Close"]
    except Exception as e:
        st.error(f"🚫 {assets[symbol]} 抓取資料時發生錯誤：{e}")

if data:
    price_df = pd.DataFrame(data)

    st.subheader("📈 標準化價格走勢比較")
    fig, ax = plt.subplots(figsize=(12, 5))

    for symbol in price_df.columns:
        series = price_df[symbol].dropna()
        if series.empty:
            st.warning(f"⚠️ {assets[symbol]} 沒有有效數據，無法繪圖。")
            continue
        try:
            normalized = series / series.iloc[0]
            ax.plot(normalized.index, normalized, label=assets[symbol])
        except IndexError:
            st.warning(f"⚠️ {assets[symbol]} 的資料不足，無法繪圖。")

    title_text = f"Normalized Price Trend (Past 180 Days)\nLast Updated: {fetch_time}"
    ax.set_title(title_text, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized Price")
    ax.legend(loc="upper left")
    ax.grid(True)
    st.pyplot(fig)

    # 計算日報酬與相關性（資料對齊）
    returns_df = price_df.pct_change().dropna(how="any")
    if not returns_df.empty:
        correlation = returns_df.corr()
        st.subheader(f"🔗 日報酬率相關係數 （最後更新：{fetch_time}）")
        st.dataframe(correlation.round(3))
    else:
        st.warning("⚠️ 沒有足夠的資料來計算相關性。")
else:
    st.error("🚫 無法取得任何資產的資料。請檢查網路或資產代碼。")
