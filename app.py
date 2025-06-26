
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
    if hist.empty:
        st.warning(f"{assets[symbol]} 的資料無法抓取，請稍後再試或檢查代碼。")
    else:
        data[symbol] = hist["Close"]

# 如果有資料，則進行後續分析
if data:
    price_df = pd.DataFrame(data)

    # 畫價格線圖（標準化）
    st.subheader("📈 標準化價格走勢比較")
    fig, ax = plt.subplots(figsize=(12, 5))
    for symbol in data.keys():
        ax.plot(price_df.index, price_df[symbol] / price_df[symbol].iloc[0], label=assets[symbol])
    ax.set_title("Normalized Price Trend (Past 180 Days)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized Price")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # 計算日報酬與相關性
    returns_df = price_df.pct_change().dropna()
    correlation = returns_df.corr()

    st.subheader("🔗 日報酬率相關係數")
    st.dataframe(correlation.round(3))
else:
    st.error("無法取得任何資產的資料。")
