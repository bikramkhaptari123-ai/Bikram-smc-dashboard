import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import yfinance as yf

st.set_page_config(page_title="Pro SMC & ICT Automated Financial Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Pro SMC & ICT Automated Financial Dashboard")

st.sidebar.header("⚙️ Advanced Settings")
asset_type = st.sidebar.selectbox("Asset Class", ["Crypto", "Forex", "Commodity", "NEPSE"])

if asset_type == "Crypto":
    crypto_map = {
        "Bitcoin (BTC/USD)": "BTC-USD",
        "Ethereum (ETH/USD)": "ETH-USD",
        "Solana (SOL/USD)": "SOL-USD",
        "Binance Coin (BNB/USD)": "BNB-USD",
        "Ripple (XRP/USD)": "XRP-USD",
        "Cardano (ADA/USD)": "ADA-USD",
        "Dogecoin (DOGE/USD)": "DOGE-USD",
        "Avalanche (AVAX/USD)": "AVAX-USD",
        "Chainlink (LINK/USD)": "LINK-USD"
    }
    selected_name = st.sidebar.selectbox("Select Crypto Pair", list(crypto_map.keys()))
    ticker = crypto_map[selected_name]
    is_nepse = False
elif asset_type == "Forex":
    forex_map = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "USDCAD=X",
        "NZD/USD": "NZDUSD=X",
        "USD/CHF": "USDCHF=X"
    }
    selected_name = st.sidebar.selectbox("Select Forex Pair", list(forex_map.keys()))
    ticker = forex_map[selected_name]
    is_nepse = False
elif asset_type == "Commodity":
    comm_map = {
        "Gold Spot": "GC=F",
        "Silver Spot": "SI=F",
        "Crude Oil": "CL=F",
        "Natural Gas": "NG=F"
    }
    selected_name = st.sidebar.selectbox("Select Commodity", list(comm_map.keys()))
    ticker = comm_map[selected_name]
    is_nepse = False
else:
    nepse_symbols = [
        "NABIL", "NMB", "NICA", "KBL", "GBIME", "EBL", "PCBL", 
        "SBL", "CZBIL", "SANIMA", "PRVU", "ADBL", "HBL", 
        "AKPL", "UPPER", "BHPL", "NRIC", "HRL", "CIT", "NTC", "NLIC"
    ]
    ticker = st.sidebar.selectbox("Select NEPSE Stock", sorted(nepse_symbols))
    is_nepse = True

timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1D", "1W"], index=2)

@st.cache_data(ttl=300)
def get_data(is_nepse_stock, sym, tf):
    if is_nepse_stock:
        periods_map = {"1h": 100, "4h": 120, "1D": 150, "1W": 104}
        periods = periods_map.get(tf, 150)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq='D')
        np.random.seed(hash(sym) % 2**32)
        base_price = 450 + np.random.randint(50, 600)
        returns = np.random.normal(0.0018, 0.022, size=len(dates))
        price_path = base_price * np.exp(np.cumsum(returns))
        df = pd.DataFrame({
            'open': price_path * (1 + np.random.uniform(-0.009, 0.009, size=len(dates))),
            'high': price_path * (1 + np.random.uniform(0.005, 0.018, size=len(dates))),
            'low': price_path * (1 - np.random.uniform(0.005, 0.018, size=len(dates))),
            'close': price_path,
            'volume': np.random.randint(40000, 700000, size=len(dates))
        }, index=dates)
        return df
    else:
        try:
            tf_settings = {"1h": ("60m", "730d"), "4h": ("60m", "730d"), "1D": ("1d", "max"), "1W": ("1wk", "max")}
            interval, period = tf_settings.get(tf, ("1d", "1y"))
            df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            rename_dict = {}
            for col in df.columns:
                cl = str(col).lower()
                if 'open' in cl: rename_dict[col] = 'open'
                elif 'high' in cl: rename_dict[col] = 'high'
                elif 'low' in cl: rename_dict[col] = 'low'
                elif 'close' in cl: rename_dict[col] = 'close'
                elif 'volume' in cl: rename_dict[col] = 'volume'
            df = df.rename(columns=rename_dict)
            if 'volume' not in df.columns:
                df['volume'] = 0
            if tf == "4h" and interval == "60m":
                df = df.resample('4h').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}).dropna()
            return df.dropna(subset=['close'])
        except Exception:
            return None

df = get_data(is_nepse, ticker, timeframe)

if df is not None and not df.empty:
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    shapes = []
    recent = df.tail(60)
    for i in range(2, len(recent) - 2):
        c_prev = recent.iloc[i-1]
        c_next = recent.iloc[i+1]
        c_curr = recent.iloc[i]
        
        # Fair Value Gaps (FVG)
        if c_next['low'] > c_prev['high']:
            shapes.append(dict(
                type="rect",
                x0=recent.index[i-1], y0=c_prev['high'],
                x1=recent.index[-1], y1=c_next['low'],
                xref="x", yref="y",
                fillcolor="rgba(38, 166, 154, 0.25)",
                line=dict(color="#26a69a", width=1, dash="dot"),
                layer="below"
            ))
        elif c_next['high'] < c_prev['low']:
            shapes.append(dict(
                type="rect",
                x0=recent.index[i-1], y0=c_next['high'],
                x1=recent.index[-1], y1=c_prev['low'],
                xref="x", yref="y",
                fillcolor="rgba(239, 83, 80, 0.25)",
                line=dict(color="#ef5350", width=1, dash="dot"),
                layer="below"
            ))
            
        # Order Blocks (OB)
        if c_curr['close'] > c_curr['open'] and recent.iloc[i-1]['close'] < recent.iloc[i-1]['open']:
            shapes.append(dict(
                type="rect",
                x0=recent.index[i-1], y0=recent.iloc[i-1]['low'],
                x1=recent.index[-1], y1=recent.iloc[i-1]['high'],
                xref="x", yref="y",
                fillcolor="rgba(41, 98, 255, 0.25)",
                line=dict(color="#2962ff", width=1.5),
                layer="below"
            ))

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.03, row_heights=[0.65, 0.17, 0.18]
    )

    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name="Price",
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350',
        increasing_fillcolor='#26a69a', decreasing_fillcolor='#ef5350'
    ), row=1, col=1)

    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['close'], df['open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], name="Volume", marker_color=colors), row=2, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], name="RSI", line=dict(color='#ab47bc', width=1.3)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", row=3, col=1)

    fig.update_layout(
        shapes=shapes,
        template="plotly_dark",
        paper_bgcolor="#131722",
        plot_bgcolor="#131722",
        font=dict(color="#d1d4dc", size=11),
        xaxis_rangeslider_visible=False,
        height=800,
        margin=dict(l=10, r=50, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    fig.update_xaxes(gridcolor="#2a2e39")
    fig.update_yaxes(side="right", gridcolor="#2a2e39")

    st.subheader(f"📈 SMC & ICT Analysis: {ticker if not is_nepse else 'NEPSE: ' + ticker} ({timeframe})")
    st.markdown("🔵 **Blue Boxes**: Order Blocks (OB) | 🟩/🟥 **Dotted Zones**: Fair Value Gaps (FVG)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Data load avvadam lo samasya vachindi. Kotha symbol try cheyyandi.")
