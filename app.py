
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="BTC、黃金ETF 與高相關美股分析", layout="wide")

st.title("📊 BTC、黃金ETF(GLD) 與高相關美股走勢 + 相關性分析")

assets = {
    "BTC-USD": "Bitcoin",
    "COIN": "Coinbase",
    "MSTR": "MicroStrategy",
    "GLD": "Gold ETF (GLD)"
}

st.markdown("資料來源：Yahoo Finance | 期間：過去 180 天")

# 抓資料
data = {}
for symbol in assets:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="180d")
    if hist.empty or hist["Close"].dropna().empty:
        st.warning(f"⚠️ {assets[symbol]} 的資料無法抓取，請稍後再試。")
    else:
        data[symbol] = hist["Close"]

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

    ax.set_title("Normalized Price Trend (Past 180 Days)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized Price")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # 計算日報酬與相關性（資料對齊）
    returns_df = price_df.pct_change().dropna(how="any")
    if not returns_df.empty:
        correlation = returns_df.corr()
        st.subheader("🔗 日報酬率相關係數")
        st.dataframe(correlation.round(3))
    else:
        st.warning("⚠️ 沒有足夠的資料來計算相關性。")
else:
    st.error("🚫 無法取得任何資產的資料。請檢查網路或資產代碼。")
