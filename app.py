import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import ccxt
import yfinance as yf
import numpy as np

st.set_page_config(page_title="Pro TradingView SMC Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Pro TradingView SMC Dashboard (With Volume & RSI)")

# Sidebar Controls
st.sidebar.header("⚙️ Dashboard Settings")
theme_choice = st.sidebar.selectbox("Theme Mode", ["TradingView Dark", "TradingView Light"], index=0)
asset_class = st.sidebar.selectbox("Asset Class", ["Crypto", "NEPSE", "Exness Watchlist"])

# Asset Selection and Ticker mapping
if asset_class == "Crypto":
    crypto_map = {
        "BTC/USDT": "BTC-USD",
        "ETH/USDT": "ETH-USD",
        "SOL/USDT": "SOL-USD",
        "BNB/USDT": "BNB-USD",
        "XRP/USDT": "XRP-USD",
        "ADA/USDT": "ADA-USD",
        "DOGE/USDT": "DOGE-USD",
        "AVAX/USDT": "AVAX-USD",
        "DOT/USDT": "DOT-USD",
        "LINK/USDT": "LINK-USD"
    }
    symbol = st.sidebar.selectbox("Select Crypto Pair", list(crypto_map.keys()))
    yf_symbol = crypto_map[symbol]
elif asset_class == "NEPSE":
    nepse_symbol = st.sidebar.text_input("Enter NEPSE Symbol (e.g., NABIL, NICA)", "NABIL")
    yf_symbol = f"{nepse_symbol}.NE" if not nepse_symbol.endswith(".NE") else nepse_symbol
else:
    exness_map = {
        "Gold (XAU/USD)": "GC=F",
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X"
    }
    symbol = st.sidebar.selectbox("Select Exness Asset", list(exness_map.keys()))
    yf_symbol = exness_map[symbol]

timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d", "1wk"], index=1)

# Technical Calculations (RSI & Indicators)
def calculate_indicators(df):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Moving Averages (EMA 20 & 50)
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    return df

# Data Fetching Function
@st.cache_data(ttl=300)
def fetch_data(ticker, tf):
    try:
        period_map = {"1h": "60d", "4h": "60d", "1d": "1y", "1wk": "2y"}
        interval_map = {"1h": "60m", "4h": "1h", "1d": "1d", "1wk": "1wk"} # yfinance limitation for 4h uses hourly or daily
        
        per = period_map.get(tf, "60d")
        iv = "1h" if tf == "4h" else interval_map.get(tf, "1d")
        
        data = yf.download(ticker, period=per, interval=iv, progress=False)
        if data.empty:
            return None
        
        # Flatten multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        data = data.rename(columns={
            'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
        })
        
        # Resample to 4h if selected timeframe is 4h and interval was hourly
        if tf == "4h" and len(data) > 0:
            data = data.resample('4h').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()

        data = data.dropna()
        return calculate_indicators(data)
    except Exception as e:
        return None

# Load Data
st.info(f"Loading data for {yf_symbol} ({timeframe})...")
df = fetch_data(yf_symbol, timeframe)

if df is not None and not df.empty:
    # Theme configuration
    is_dark = (theme_choice == "TradingView Dark")
    bg_color = "#131722" if is_dark else "#ffffff"
    text_color = "#d1d4dc" if is_dark else "#191919"
    grid_color = "#2a2e39" if is_dark else "#e1e3e6"

    # Plotly Subplots (Candlestick + Volume + RSI)
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=[0.6, 0.2, 0.2]
    )

    # 1. Candlestick & EMAs
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name="Price", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['ema20'], name="EMA 20", line=dict(color='#2962ff', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema50'], name="EMA 50", line=dict(color='#ff9800', width=1.5)), row=1, col=1)

    # 2. Volume Bar Chart
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['close'], df['open'])]
    fig.add_trace(go.Bar(
        x=df.index, y=df['volume'], name="Volume", marker_color=colors
    ), row=2, col=1)

    # 3. RSI Indicator
    fig.add_trace(go.Scatter(
        x=df.index, y=df['rsi'], name="RSI (14)", line=dict(color='#ab47bc', width=1.5)
    ), row=3, col=1)

    # RSI Overbought/Oversold reference lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    # Layout styling
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        xaxis_rangeslider_visible=False,
        height=750,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )

    fig.update_xaxes(gridcolor=grid_color)
    fig.update_yaxes(gridcolor=grid_color)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"Data not found for {yf_symbol}. Please check the symbol name or try another timeframe.")
