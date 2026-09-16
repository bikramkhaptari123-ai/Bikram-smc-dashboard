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

st.title("📈 Pro TradingView SMC Dashboard (With Volume & RSI)")

# Sidebar Controls
st.sidebar.header("⚙️ Dashboard Settings")
theme_choice = st.sidebar.radio("Theme Mode", ["TradingView Light", "TradingView Dark"], index=0)
asset_class = st.sidebar.selectbox("Asset Class", ["Crypto", "NEPSE", "Exness Watchlist"])

# Technical Calculations (RSI & Indicators)
def calculate_indicators(df):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

# SMC Pattern Detector (FVG, OB, BOS)
def detect_smc_structures(df):
    fvg_list = []
    ob_list = []
    bos_list = []

    for i in range(2, len(df)):
        # FVG
        if df['low'].iloc[i] > df['high'].iloc[i-2]:
            fvg_list.append({'type': 'Bullish FVG', 'time': df['timestamp_str'].iloc[i-1], 'top': df['low'].iloc[i], 'bottom': df['high'].iloc[i-2]})
        elif df['high'].iloc[i] < df['low'].iloc[i-2]:
            fvg_list.append({'type': 'Bearish FVG', 'time': df['timestamp_str'].iloc[i-1], 'top': df['low'].iloc[i-2], 'bottom': df['high'].iloc[i]})

    for i in range(2, len(df)-1):
        # Order Block
        if df['close'].iloc[i-1] < df['open'].iloc[i-1] and df['close'].iloc[i] > df['high'].iloc[i-1]:
            ob_list.append({'type': 'Bullish OB', 'time': df['timestamp_str'].iloc[i-1], 'top': df['high'].iloc[i-1], 'bottom': df['low'].iloc[i-1]})
        elif df['close'].iloc[i-1] > df['open'].iloc[i-1] and df['close'].iloc[i] < df['low'].iloc[i-1]:
            ob_list.append({'type': 'Bearish OB', 'time': df['timestamp_str'].iloc[i-1], 'top': df['high'].iloc[i-1], 'bottom': df['low'].iloc[i-1]})

        # BOS (Break of Structure)
        if i > 5 and df['close'].iloc[i] > df['high'].iloc[i-5:i-1].max():
            bos_list.append({'type': 'BOS', 'time': df['timestamp_str'].iloc[i], 'price': df['high'].iloc[i]})
        elif i > 5 and df['close'].iloc[i] < df['low'].iloc[i-5:i-1].min():
            bos_list.append({'type': 'CHoCH', 'time': df['timestamp_str'].iloc[i], 'price': df['low'].iloc[i]})

    return fvg_list, ob_list, bos_list

# Realistic NEPSE Generator with Volume
def generate_nepse_data(symbol):
    np.random.seed(abs(hash(symbol)) % (2**32))
    base_prices = {"NABIL": 610.0, "NMB": 255.0, "NICA": 460.0, "KBL": 195.0, "AKPL": 325.0, "BHPL": 290.0, "UPPER": 245.0}
    start_p = base_prices.get(symbol, 300.0)
    
    dates = pd.date_range(end=pd.Timestamp.today(), periods=80, freq='B')
    t = np.linspace(0, 3*np.pi, 80)
    close_prices = start_p + np.sin(t) * (start_p * 0.08) + np.cumsum(np.random.normal(0, start_p * 0.008, 80))
    
    opens, highs, lows, volumes = [], [], [], []
    for i in range(80):
        prev_c = close_prices[i-1] if i > 0 else start_p
        o = prev_c * (1 + np.random.uniform(-0.003, 0.003))
        c = close_prices[i]
        h = max(o, c) + abs(np.random.normal(0, start_p * 0.005))
        l = min(o, c) - abs(np.random.normal(0, start_p * 0.005))
        vol = int(np.random.uniform(50000, 400000))
        
        opens.append(o)
        highs.append(h)
        lows.append(l)
        volumes.append(vol)
        
    df = pd.DataFrame({'timestamp': dates, 'open': opens, 'high': highs, 'low': lows, 'close': close_prices, 'volume': volumes})
    df['timestamp_str'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    return df

# Main Pro TradingView Chart Renderer
def render_pro_chart(df, symbol, show_smc, show_rsi, theme):
    df = calculate_indicators(df)
    
    # Theme Colors
    if theme == "TradingView Light":
        bg_color, grid_color, text_color = "#FFFFFF", "#F0F3FA", "#131722"
        up_color, down_color = "#089981", "#F23645"
        vol_up, vol_down = "rgba(8, 153, 129, 0.3)", "rgba(242, 54, 69, 0.3)"
    else:
        bg_color, grid_color, text_color = "#131722", "#2A2E39", "#B2B5BE"
        up_color, down_color = "#089981", "#F23645"
        vol_up, vol_down = "rgba(8, 153, 129, 0.4)", "rgba(242, 54, 69, 0.4)"

    rows = 2 if show_rsi else 1
    heights = [0.75, 0.25] if show_rsi else [1.0]

    fig = make_subplots(
        rows=rows, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03,
        row_heights=heights,
        specs=[[{"secondary_y": True}]] + ([[{ "secondary_y": False}]] if show_rsi else [])
    )

    # 1. Main Candlestick Chart
    fig.add_trace(go.Candlestick(
        x=df['timestamp_str'],
        open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        increasing_fillcolor=up_color, increasing_line_color=up_color,
        decreasing_fillcolor=down_color, decreasing_line_color=down_color,
        name="Price"
    ), row=1, col=1, secondary_y=False)

    # 2. Volume Bars Overlay (Inside Main Chart Bottom)
    vol_colors = [vol_up if c >= o else vol_down for c, o in zip(df['close'], df['open'])]
    fig.add_trace(go.Bar(
        x=df['timestamp_str'], y=df['volume'],
        marker_color=vol_colors,
        name="Volume", showlegend=False
    ), row=1, col=1, secondary_y=True)

    # Secondary Y-Axis Scaling for Volume Overlay
    fig.update_yaxes(range=[0, df['volume'].max() * 4], showticklabels=False, secondary_y=True, row=1, col=1)

    # 3. SMC Zones & BOS Annotation
    if show_smc:
        fvgs, obs, bos_list = detect_smc_structures(df)
        
        # Plot Order Blocks
        for ob in obs[-3:]:
            color = "rgba(41, 98, 255, 0.25)" if ob['type'] == 'Bullish OB' else "rgba(255, 152, 0, 0.25)"
            fig.add_shape(type="rect", x0=ob['time'], x1=df['timestamp_str'].iloc[-1], y0=ob['bottom'], y1=ob['top'], fillcolor=color, line=dict(width=0), row=1, col=1)

        # Plot BOS / CHoCH Labels
        for b in bos_list[-3:]:
            fig.add_annotation(
                x=b['time'], y=b['price'], text=f"<b>{b['type']}</b>",
                showarrow=True, arrowhead=1, arrowcolor="#089981" if b['type']=='BOS' else "#F23645",
                font=dict(size=10, color=text_color), row=1, col=1
            )

    # 4. RSI Subplot
    if show_rsi:
        fig.add_trace(go.Scatter(x=df['timestamp_str'], y=df['rsi'], line=dict(color='#7E57C2', width=1.5), name="RSI"), row=2, col=1)
        fig.add_shape(type="line", x0=df['timestamp_str'].iloc[0], x1=df['timestamp_str'].iloc[-1], y0=70, y1=70, line=dict(color="#F23645", dash="dash"), row=2, col=1)
        fig.add_shape(type="line", x0=df['timestamp_str'].iloc[0], x1=df['timestamp_str'].iloc[-1], y0=30, y1=30, line=dict(color="#089981", dash="dash"), row=2, col=1)
        fig.update_yaxes(title_text="RSI (14)", range=[0, 100], row=2, col=1)

    # Styling & Layout
    fig.update_layout(
        paper_bgcolor=bg_color, plot_bgcolor=bg_color,
        height=720, margin=dict(l=10, r=80, t=20, b=20),
        xaxis_rangeslider_visible=False,
        hovermode="x unified"
    )

    fig.update_yaxes(side="right", showgrid=True, gridcolor=grid_color, tickfont=dict(color=text_color, size=11), secondary_y=False)
    fig.update_xaxes(type="category", showgrid=True, gridcolor=grid_color, tickfont=dict(color=text_color, size=10), nticks=12)

    st.plotly_chart(fig, use_container_width=True)

# Selection Controls
col1, col2 = st.columns([1, 4])
with col1:
    st.subheader("Indicators")
    show_smc = st.checkbox("Show SMC (OB/BOS)", value=True)
    show_rsi = st.checkbox("Show RSI Indicator", value=True)

    if asset_class == "Crypto":
        symbol = st.selectbox("Crypto Pair", ["ETH/USDT", "BTC/USDT", "SOL/USDT"])
        timeframe = st.selectbox("Timeframe", ["15m", "1h", "4h"], index=1)
    elif asset_class == "NEPSE":
        symbol = st.selectbox("NEPSE Symbol", ["NMB", "NABIL", "NICA", "KBL", "AKPL"])
    else:
        symbol = st.selectbox("Exness Asset", ["GC=F", "EURUSD=X"])

# Data Fetching & Execution
if asset_class == "Crypto":
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp_str'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%m-%d %H:%M')
    render_pro_chart(df, symbol, show_smc, show_rsi, theme_choice)

elif asset_class == "NEPSE":
    df = generate_nepse_data(symbol)
    render_pro_chart(df, f"NEPSE:{symbol}", show_smc, show_rsi, theme_choice)

else:
    data = yf.download(symbol, period="1mo", interval="1h")
    if not data.empty:
        df = data.reset_index()
        df.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in df.columns]
        time_col = 'datetime' if 'datetime' in df.columns else 'date'
        df['timestamp_str'] = pd.to_datetime(df[time_col]).dt.strftime('%m-%d %H:%M')
        render_pro_chart(df, symbol, show_smc, show_rsi, theme_choice)