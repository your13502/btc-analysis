
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pytz
import numpy as np

# 頁面設定
st.set_page_config(page_title="Asset Analysis Dashboard", layout="wide")

# ✅ 語言設定
language = st.sidebar.selectbox(
    "Language / 語言 / 言語",
    options=["English", "中文 (繁體)", "中文 (简体)", "日本語"],
    index=0
)

# ✅ 多語字典
text = {
    "title": {
        "English": "Asset Analysis Dashboard",
        "中文 (繁體)": "資產分析儀表板",
        "中文 (简体)": "资产分析仪表板",
        "日本語": "資産分析ダッシュボード"
    },
    "normalized_price_trend": {
        "English": "Normalized Price Trend",
        "中文 (繁體)": "標準化價格走勢",
        "中文 (简体)": "标准化价格走势",
        "日本語": "正規化価格トレンド"
    },
    "correlation_heatmap": {
        "English": "Correlation Heatmap",
        "中文 (繁體)": "相關性熱力圖",
        "中文 (简体)": "相关性热力图",
        "日本語": "相関ヒートマップ"
    },
    "select_assets": {
        "English": "Select Assets",
        "中文 (繁體)": "選擇資產",
        "中文 (简体)": "选择资产",
        "日本語": "資産を選択"
    },
    "time_range": {
        "English": "Select Time Range",
        "中文 (繁體)": "選擇時間範圍",
        "中文 (简体)": "选择时间范围",
        "日本語": "期間を選択"
    },
    "theme_mode": {
        "English": "Theme Mode",
        "中文 (繁體)": "主題模式",
        "中文 (简体)": "主题模式",
        "日本語": "テーマモード"
    },
    "last_updated": {
        "English": "Last Updated",
        "中文 (繁體)": "最後更新",
        "中文 (简体)": "最后更新",
        "日本語": "最終更新"
    },
    "no_data": {
        "English": "⚠️ No data available for selected assets and time range.",
        "中文 (繁體)": "⚠️ 選擇的資產或時間範圍沒有數據。",
        "中文 (简体)": "⚠️ 选择的资产或时间范围没有数据。",
        "日本語": "⚠️ 選択された資産または期間にデータがありません。"
    }
}

st.title(text["title"][language])

# 資產選單
asset_options = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    "TSLA": "Tesla",
    "SPY": "S&P500 ETF",
    "GLD": "Gold ETF",
    "COIN": "Coinbase",
    "MSTR": "MicroStrategy"
}

selected_assets = st.sidebar.multiselect(
    text["select_assets"][language],
    options=list(asset_options.keys()),
    default=["BTC-USD", "ETH-USD", "SPY", "GLD"],
    format_func=lambda x: asset_options[x]
)

if not selected_assets:
    st.warning(text["no_data"][language])
    st.stop()

# 時間範圍
time_range = st.sidebar.selectbox(
    text["time_range"][language],
    options=["7 Days", "30 Days", "180 Days", "365 Days"],
    index=3
)
time_map = {
    "7 Days": 7,
    "30 Days": 30,
    "180 Days": 180,
    "365 Days": 365
}
days = time_map[time_range]

# 主題
theme = st.sidebar.radio(text["theme_mode"][language], ["Light", "Dark"], index=0)
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

# 抓資料
end_date = datetime.today()
start_date = end_date - timedelta(days=days)
fetch_time_utc = datetime.utcnow()
local_timezone = pytz.timezone("Asia/Taipei")
fetch_time_local = fetch_time_utc.astimezone(local_timezone).strftime("%Y-%m-%d %H:%M:%S")

data = {}
for symbol in selected_assets:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    if not hist.empty:
        data[symbol] = hist["Close"]

if not data:
    st.warning(text["no_data"][language])
    st.stop()

# 對齊資料 + 補空值
price_df = pd.DataFrame(data).ffill().bfill()
if price_df.empty:
    st.warning(text["no_data"][language])
    st.stop()

returns = price_df.pct_change().dropna()

# 📈 Normalized Price Trend
st.subheader(text["normalized_price_trend"][language])
fig, ax = plt.subplots(figsize=(12, 5))
for symbol in price_df.columns:
    norm = price_df[symbol] / price_df[symbol].iloc[0]
    ax.plot(norm.index, norm, label=asset_options[symbol])

ax.set_title(f"{text['normalized_price_trend'][language]} (Past {time_range})", fontsize=14, color=text_color)
ax.set_xlabel("Date", color=text_color)
ax.set_ylabel("Normalized Price", color=text_color)
ax.legend(loc="upper left")
ax.grid(True, color=grid_color)
ax.set_facecolor(background_color)
ax.tick_params(colors=text_color)
ax.text(1.0, 1.02, f"{text['last_updated'][language]}: {fetch_time_local}",
        transform=ax.transAxes, ha='right', va='bottom', fontsize=6, color=text_color)
st.pyplot(fig)

# 🔥 Correlation Heatmap
st.subheader(text["correlation_heatmap"][language])
corr = returns.corr()

# 數值顯示處理
corr_display = corr.applymap(lambda x: 0 if abs(x) < 0.005 else round(x, 2))

# Heatmap
size = max(6, len(corr) * 1.2)
fig2, ax2 = plt.subplots(figsize=(size, size))

sns.heatmap(
    corr,
    annot=corr_display,
    cmap="coolwarm",
    fmt="",
    ax=ax2,
    square=True,
    cbar=False
)

# Colorbar 放底部
cbar = fig2.colorbar(
    ax2.collections[0],
    orientation="horizontal",
    fraction=0.05,
    pad=0.1,
    aspect=30
)
cbar.ax.tick_params(labelsize=8)
st.pyplot(fig2)
