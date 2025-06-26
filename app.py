
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pytz
import numpy as np

# ✅ 頁面配置
st.set_page_config(page_title="Asset Analysis Dashboard", layout="wide")

# ✅ 語言選擇
language = st.sidebar.selectbox(
    "Language / 語言 / 言語",
    options=["English", "中文 (繁體)", "中文 (简体)", "日本語"],
    index=0
)

# ✅ 文本對應
text = {
    "title": {
        "English": "Asset Analysis Dashboard",
        "中文 (繁體)": "資產分析儀表板",
        "中文 (简体)": "资产分析仪表板",
        "日本語": "資産分析ダッシュボード"
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
    "theme": {
        "English": "Theme Mode",
        "中文 (繁體)": "主題模式",
        "中文 (简体)": "主题模式",
        "日本語": "テーマモード"
    },
    "overview": {
        "English": "Overview",
        "中文 (繁體)": "總覽",
        "中文 (简体)": "总览",
        "日本語": "概要"
    },
    "tech_analysis": {
        "English": "Technical Analysis",
        "中文 (繁體)": "技術分析",
        "中文 (简体)": "技术分析",
        "日本語": "テクニカル分析"
    },
    "correlation": {
        "English": "Correlation",
        "中文 (繁體)": "相關性分析",
        "中文 (简体)": "相关性分析",
        "日本語": "相関分析"
    },
    "backtest": {
        "English": "Backtest",
        "中文 (繁體)": "回測模擬",
        "中文 (简体)": "回测模拟",
        "日本語": "バックテスト"
    },
    "last_updated": {
        "English": "Last Updated",
        "中文 (繁體)": "最後更新",
        "中文 (简体)": "最后更新",
        "日本語": "最終更新"
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

# 深色模式
theme = st.sidebar.radio(text["theme"][language], ["Light", "Dark"], index=0)

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

# 資料抓取
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

price_df = pd.DataFrame(data)
returns = price_df.pct_change().dropna()

# ✅ 分頁設計
tabs = st.tabs([
    f"🏠 {text['overview'][language]}",
    f"📈 {text['tech_analysis'][language]}",
    f"💰 {text['correlation'][language]}",
    f"📊 {text['backtest'][language]}"
])

# 🏠 總覽
with tabs[0]:
    st.subheader(text['overview'][language])

    if not price_df.empty:
        fig, ax = plt.subplots(figsize=(12, 5))
        for symbol in price_df.columns:
            norm = price_df[symbol] / price_df[symbol].iloc[0]
            ax.plot(norm.index, norm, label=asset_options[symbol])

        ax.set_title(f"Normalized Price Trend (Past {time_range})", fontsize=14, color=text_color)
        ax.set_xlabel("Date", color=text_color)
        ax.set_ylabel("Normalized Price", color=text_color)
        ax.legend(loc="upper left")
        ax.grid(True, color=grid_color)
        ax.set_facecolor(background_color)
        ax.tick_params(colors=text_color)
        ax.text(1.0, 1.02, f"{text['last_updated'][language]}: {fetch_time_local}",
                transform=ax.transAxes, ha='right', va='bottom', fontsize=6, color=text_color)

        st.pyplot(fig)

        st.subheader("Correlation Table")
        corr = returns.corr()
        st.dataframe(corr.round(3))

        st.subheader("Correlation Heatmap")
        fig2, ax2 = plt.subplots()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax2)
        st.pyplot(fig2)
    else:
        st.warning("No data available.")

# 📈 技術分析
with tabs[1]:
    for symbol in price_df.columns:
        st.markdown(f"### {asset_options[symbol]}")
        df = price_df[symbol].dropna()
        ma20 = df.rolling(window=20).mean()
        ma50 = df.rolling(window=50).mean()

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df.index, df, label="Price")
        ax.plot(ma20.index, ma20, label="MA20")
        ax.plot(ma50.index, ma50, label="MA50")

        ax.set_title(f"{asset_options[symbol]} with MA20/MA50", fontsize=12, color=text_color)
        ax.set_xlabel("Date", color=text_color)
        ax.set_ylabel("Price", color=text_color)
        ax.legend()
        ax.grid(True, color=grid_color)
        ax.set_facecolor(background_color)
        ax.tick_params(colors=text_color)
        st.pyplot(fig)

# 💰 相關性分析
with tabs[2]:
    st.subheader(text['correlation'][language])
    if not returns.empty:
        st.dataframe(returns.corr().round(3))
    else:
        st.warning("No data available.")

# 📊 回測
with tabs[3]:
    st.subheader(text['backtest'][language])
    for symbol in price_df.columns:
        st.markdown(f"### {asset_options[symbol]}")
        df = price_df[symbol].dropna()
        ma20 = df.rolling(window=20).mean()
        ma50 = df.rolling(window=50).mean()

        signal = (ma20 > ma50).astype(int)
        backtest_returns = df.pct_change().shift(-1) * signal.shift(1)
        cumulative = (1 + backtest_returns.fillna(0)).cumprod()

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(cumulative.index, cumulative, label="Backtest Cumulative Return")

        ax.set_title(f"{asset_options[symbol]} MA20/MA50 Backtest", fontsize=12, color=text_color)
        ax.set_xlabel("Date", color=text_color)
        ax.set_ylabel("Cumulative Return", color=text_color)
        ax.legend()
        ax.grid(True, color=grid_color)
        ax.set_facecolor(background_color)
        ax.tick_params(colors=text_color)
        st.pyplot(fig)
