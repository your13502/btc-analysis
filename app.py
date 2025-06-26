
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz

# ✅ HTML 自動刷新，每5分鐘
refresh_interval = 5 * 60  # 秒
refresh_code = f"""
    <meta http-equiv="refresh" content="{refresh_interval}">
"""
st.markdown(refresh_code, unsafe_allow_html=True)

st.set_page_config(page_title="資產價格走勢與相關性分析", layout="wide")

st.title("📊 資產價格走勢與相關性分析")

# 資產選單
asset_options = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "TSLA": "Tesla",
    "SPY": "S&P500 ETF",
    "GLD": "Gold ETF",
    "COIN": "Coinbase",
    "MSTR": "MicroStrategy"
}

selected_assets = st.multiselect(
    "選擇你想分析的資產：",
    options=list(asset_options.keys()),
    default=["BTC-USD", "COIN", "MSTR", "GLD"],
    format_func=lambda x: asset_options[x]
)

# 深色模式選擇
theme = st.radio("選擇主題模式：", ["Light", "Dark"], index=0)

if theme == "Dark":
    plt.style.use('dark_background')
    background_color = '#0e1117'
    grid_color = 'gray'
    text_color = 'white'
else:
    plt.style.use('default')
    background_color = 'white'
    grid_color = 'lightgray'
    text_color = 'black'

st.markdown("資料來源：Yahoo Finance | 期間：過去 365 天")

# 設定日期範圍為365天
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# 顯示資料抓取的時間（本地時間）
fetch_time_utc = datetime.utcnow()
local_timezone = pytz.timezone("Asia/Taipei")  # 根據需要修改時區
fetch_time_local = fetch_time_utc.astimezone(local_timezone).strftime("%Y-%m-%d %H:%M:%S")

# 抓資料
data = {}
for symbol in selected_assets:
    ticker = yf.Ticker(symbol)
    try:
        hist = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        if hist.empty or hist["Close"].dropna().empty:
            st.warning(f"⚠️ {asset_options[symbol]} 的資料無法抓取，請稍後再試。")
        else:
            data[symbol] = hist["Close"]
    except Exception as e:
        st.error(f"🚫 {asset_options[symbol]} 抓取資料時發生錯誤：{e}")

if data:
    price_df = pd.DataFrame(data)

    st.subheader("📈 標準化價格走勢比較")
    fig, ax = plt.subplots(figsize=(12, 5), facecolor=background_color)
    fig.patch.set_facecolor(background_color)

    for symbol in price_df.columns:
        series = price_df[symbol].dropna()
        if series.empty:
            st.warning(f"⚠️ {asset_options[symbol]} 沒有有效數據，無法繪圖。")
            continue
        try:
            normalized = series / series.iloc[0]
            ax.plot(normalized.index, normalized, label=asset_options[symbol])
        except IndexError:
            st.warning(f"⚠️ {asset_options[symbol]} 的資料不足，無法繪圖。")

    title_text = "Normalized Price Trend (Past 365 Days)"
    ax.set_title(title_text, fontsize=14, color=text_color)
    ax.set_xlabel("Date", color=text_color)
    ax.set_ylabel("Normalized Price", color=text_color)
    ax.legend(loc="upper left")
    ax.grid(True, color=grid_color)
    ax.set_facecolor(background_color)
    ax.tick_params(colors=text_color)

    # ⏰ 顯示更新時間（右上角）
    ax.text(
        1.0, 1.02,
        f"Last Updated: {fetch_time_local} (Local Time)",
        transform=ax.transAxes,
        ha='right',
        va='bottom',
        fontsize=5,
        color=text_color
    )

    st.pyplot(fig)

    # 計算日報酬與相關性（資料對齊）
    returns_df = price_df.pct_change().dropna(how="any")
    if not returns_df.empty:
        correlation = returns_df.corr()
        st.subheader(f"🔗 日報酬率相關係數 （最後更新：{fetch_time_local}）")
        st.dataframe(correlation.round(3))
    else:
        st.warning("⚠️ 沒有足夠的資料來計算相關性。")
else:
    st.error("🚫 無法取得任何資產的資料。請檢查網路或資產代碼。")
