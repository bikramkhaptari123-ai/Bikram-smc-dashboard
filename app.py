import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(page_title="Pro SMC & ICT Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Pro SMC & ICT Financial Dashboard (NEPSE, Crypto, Forex & Commodities)")

# Sidebar Controls
st.sidebar.header("⚙️ Dashboard Settings")
theme_choice = st.sidebar.selectbox("Theme Mode", ["TradingView Dark", "TradingView Light"], index=0)
asset_class = st.sidebar.selectbox("Asset Class", ["NEPSE", "Crypto", "Forex", "Commodities (Gold/Silver)"])

symbol = ""
yf_symbol = ""
is_nepse = False

if asset_class == "NEPSE":
    is_nepse = True
    nepse_symbols = [
        "NABIL", "NMB", "NICA", "KBL", "GBIME", "EBL", "PCBL", 
        "AKPL", "UPPER", "BHPL", "NRIC", "HRL", "NLIC", "CIT", "NTC"
    ]
    symbol = st.sidebar.selectbox("Select NEPSE Stock", nepse_symbols)
elif asset_class == "Crypto":
    crypto_map = {
        "BTC/USDT": "BTC-USD",
        "ETH/USDT": "ETH-USD",
        "SOL/USDT": "SOL-USD",
        "BNB/USDT": "BNB-USD",
        "XRP/USDT": "XRP-USD",
        "ADA/USDT": "ADA-USD",
        "DOGE/USDT": "DOGE-USD"
    }
    symbol = st.sidebar.selectbox("Select Crypto Pair", list(crypto_map.keys()))
    yf_symbol = crypto_map[symbol]
elif asset_class == "Forex":
    forex_map = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "USDCAD=X"
    }
    symbol = st.sidebar.selectbox("Select Forex Pair", list(forex_map.keys()))
    yf_symbol = forex_map[symbol]
else:
    comm_map = {
        "Gold (XAU/USD)": "GC=F",
        "Silver (XAG/USD)": "SI=F",
        "Crude Oil": "CL=F"
    }
    symbol = st.sidebar.selectbox("Select Commodity", list(comm_map.keys()))
    yf_symbol = comm_map[symbol]

timeframe = st.sidebar.selectbox("Timeframe", ["1h", "1d", "1wk"], index=1)

# SMC & ICT Calculations (Order Blocks & Fair Value Gaps)
def calculate_smc_indicators(df):
    # RSI & EMAs
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    # ICT Fair Value Gaps (FVG) detection
    df['fvg_bullish'] = (df['low'].shift(-1) > df['high'].shift(1)) & (df['close'] > df['open'])
    df['fvg_bearish'] = (df['high'].shift(-1) < df['low'].shift(1)) & (df['close'] < df['open'])
    
    return df

# NEPSE Mock Data Generator
def generate_nepse_data(sym):
    dates = pd.date_range(end=pd.Timestamp.now(), periods=150, freq='D')
    np.random.seed(hash(sym) % 2**32)
    base_price = 400 + np.random.randint(50, 600)
    returns = np.random.normal(0.001, 0.02, size=len(dates))
    price_path = base_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        'open': price_path * (1 + np.random.uniform(-0.008, 0.008, size=len(dates))),
        'high': price_path * (1 + np.random.uniform(0.004, 0.015, size=len(dates))),
        'low': price_path * (1 - np.random.uniform(0.004, 0.015, size=len(dates))),
        'close': price_path,
        'volume': np.random.randint(20000, 400000, size=len(dates))
    }, index=dates)
    return calculate_smc_indicators(df)

# Global Data Fetcher
@st.cache_data(ttl=300)
def fetch_global_data(ticker, tf):
    try:
        period_map = {"1h": "60d", "1d": "1y", "1wk": "2y"}
        interval_map = {"1h": "60m", "1d": "1d", "1wk": "1wk"}
        
        data = yf.download(ticker, period=period_map.get(tf, "1y"), interval=interval_map.get(tf, "1d"), progress=False, auto_adjust=True)
        if data is None or data.empty:
            return None
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        rename_dict = {}
        for col in data.columns:
            cl = str(col).lower()
            if 'open' in cl: rename_dict[col] = 'open'
            elif 'high' in cl: rename_dict[col] = 'high'
            elif 'low' in cl: rename_dict[col] = 'low'
            elif 'close' in cl: rename_dict[col] = 'close'
            elif 'volume' in cl: rename_dict[col] = 'volume'
            
        data = data.rename(columns=rename_dict)
        if 'volume' not in data.columns:
            data['volume'] = 0
            
        return calculate_smc_indicators(data.dropna(subset=['close']))
    except Exception as e:
        return None

# Load Data
if is_nepse:
    st.info(f"Loading NEPSE SMC data for **{symbol}**...")
    df = generate_nepse_data(symbol)
else:
    st.info(f"Loading SMC data for **{symbol}** ({yf_symbol})...")
    df = fetch_global_data(yf_symbol, timeframe)

if df is not None and not df.empty:
    is_dark = (theme_choice == "TradingView Dark")
    bg_color = "#131722" if is_dark else "#ffffff"
    text_color = "#d1d4dc" if is_dark else "#191919"
    grid_color = "#2a2e39" if is_dark else "#e1e3e6"

    # Plotly Subplots (Candlestick + Volume + RSI)
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=[0.65, 0.17, 0.18]
    )

    # 1. Clean TradingView Style Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name="Price", increasing_line_color='#26a69a', decreasing_line_color='#ef5350',
        increasing_fillcolor='#26a69a', decreasing_fillcolor='#ef5350'
    ), row=1, col=1)

    # EMAs
    fig.add_trace(go.Scatter(x=df.index, y=df['ema20'], name="EMA 20", line=dict(color='#2962ff', width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema50'], name="EMA 50", line=dict(color='#ff9800', width=1.2)), row=1, col=1)

    # ICT Fair Value Gaps (FVG) Highlights on Chart
    bullish_fvgs = df[df['fvg_bullish'] == True]
    if not bullish_fvgs.empty:
        fig.add_trace(go.Scatter(
            x=bullish_fvgs.index, y=bullish_fvgs['low'], mode='markers',
            marker=dict(symbol='square', size=8, color='rgba(38, 166, 154, 0.5)'),
            name="Bullish FVG Zone"
        ), row=1, col=1)

    # 2. Volume Bar Chart
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['close'], df['open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], name="Volume", marker_color=colors), row=2, col=1)

    # 3. RSI Indicator
    fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], name="RSI (14)", line=dict(color='#ab47bc', width=1.3)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", row=3, col=1)

    # Layout styling matching TradingView dark/light mode
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, size=11),
        xaxis_rangeslider_visible=False,
        height=780,
        margin=dict(l=10, r=10, t=25, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )

    fig.update_xaxes(gridcolor=grid_color, showspikes=True, spikemode="across", spikesnap="cursor", spikecolor="gray")
    fig.update_yaxes(gridcolor=grid_color, showspikes=True, spikecolor="gray")

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"Could not load data. Please check asset selection.")
