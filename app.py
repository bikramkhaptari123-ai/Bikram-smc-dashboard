import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Pro TradingView SMC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for TradingView Dark Aesthetic
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stApp { background-color: #0b0e14; color: #d1d4dc; }
    div[data-testid="stSidebar"] { background-color: #151924; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Pro SMC Financial Dashboard")

# ---------------------------------------------------------
# 1. Technical Calculations (RSI, SMC: Order Blocks & BOS/CHoCH)
# ---------------------------------------------------------
def calculate_indicators(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

def detect_smc_zones(df):
    order_blocks = []
    bos_list = []
    
    for i in range(2, len(df) - 2):
        # Bullish Order Block
        if df['Close'].iloc[i] > df['Open'].iloc[i] and df['Close'].iloc[i-1] < df['Open'].iloc[i-1]:
            if df['Close'].iloc[i] > df['High'].iloc[i-1]:
                order_blocks.append({
                    'type': 'Bullish OB',
                    'top': df['High'].iloc[i-1],
                    'bottom': df['Low'].iloc[i-1],
                    'time': df['timestamp_str'].iloc[i-1]
                })
        # Bearish Order Block
        elif df['Close'].iloc[i] < df['Open'].iloc[i] and df['Close'].iloc[i-1] > df['Open'].iloc[i-1]:
            if df['Close'].iloc[i] < df['Low'].iloc[i-1]:
                order_blocks.append({
                    'type': 'Bearish OB',
                    'top': df['High'].iloc[i-1],
                    'bottom': df['Low'].iloc[i-1],
                    'time': df['timestamp_str'].iloc[i-1]
                })
                
        # Structure Breaks (BOS / CHoCH)
        if df['High'].iloc[i] > df['High'].iloc[i-1] and df['High'].iloc[i] > df['High'].iloc[i-2]:
            bos_list.append({'type': 'BOS', 'time': df['timestamp_str'].iloc[i], 'price': df['High'].iloc[i]})
        elif df['Low'].iloc[i] < df['Low'].iloc[i-1] and df['Low'].iloc[i] < df['Low'].iloc[i-2]:
            bos_list.append({'type': 'CHoCH', 'time': df['timestamp_str'].iloc[i], 'price': df['Low'].iloc[i]})
            
    return order_blocks, bos_list

# ---------------------------------------------------------
# 2. Mock Generator for NEPSE Stocks
# ---------------------------------------------------------
def generate_nepse_data(symbol):
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D')
    np.random.seed(hash(symbol) % 2**32)
    base_price = 400 + np.random.randint(0, 500)
    returns = np.random.normal(0.001, 0.02, size=len(dates))
    price_path = base_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': price_path * (1 + np.random.uniform(-0.01, 0.01, size=len(dates))),
        'High': price_path * (1 + np.random.uniform(0.005, 0.02, size=len(dates))),
        'Low': price_path * (1 - np.random.uniform(0.005, 0.02, size=len(dates))),
        'Close': price_path,
        'Volume': np.random.randint(5000, 500000, size=len(dates))
    })
    df['timestamp_str'] = df['Date'].dt.strftime('%Y-%m-%d')
    return df

# ---------------------------------------------------------
# 3. Professional Chart Rendering Function
# ---------------------------------------------------------
def render_pro_chart(df, title, show_smc=True, show_rsi=True, theme="Dark"):
    bg_color = "#0b0e14" if theme == "Dark" else "#ffffff"
    text_color = "#d1d4dc" if theme == "Dark" else "#131722"
    grid_color = "#1e222d" if theme == "Dark" else "#f0f3fa"
    
    rows = 2 if show_rsi else 1
    row_heights = [0.8, 0.2] if show_rsi else [1.0]
    
    fig = make_subplots(
        rows=rows, cols=1, shared_xaxes=True,
        vertical_spacing=0.03, row_heights=row_heights
    )
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df['timestamp_str'], open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="Price",
        increasing_line_color="#089981", decreasing_line_color="#f23645",
        increasing_fillcolor="#089981", decreasing_fillcolor="#f23645"
    ), row=1, col=1)
    
    # SMC Zones
    if show_smc:
        order_blocks, bos_list = detect_smc_zones(df)
        for ob in order_blocks[-4:]:
            color = "rgba(8, 153, 129, 0.25)" if ob['type'] == 'Bullish OB' else "rgba(242, 54, 69, 0.25)"
            fig.add_shape(
                type="rect", x0=ob['time'], x1=df['timestamp_str'].iloc[-1],
                y0=ob['bottom'], y1=ob['top'],
                fillcolor=color, line=dict(width=0), row=1, col=1
            )
        for b in bos_list[-3:]:
            fig.add_annotation(
                x=b['time'], y=b['price'], text=f"<b>{b['type']}</b>",
                showarrow=True, arrowhead=1,
                arrowcolor="#089981" if b['type'] == 'BOS' else "#f23645",
                font=dict(size=10, color=text_color), row=1, col=1
            )
            
    # RSI Subplot
    if show_rsi and 'rsi' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp_str'], y=df['rsi'],
            line=dict(color="#7e57c2", width=1.5), name="RSI (14)"
        ), row=2, col=1)
        fig.add_shape(type="line", x0=df['timestamp_str'].iloc[0], x1=df['timestamp_str'].iloc[-1], y0=70, y1=70, line=dict(color="#f23645", dash="dash"), row=2, col=1)
        fig.add_shape(type="line", x0=df['timestamp_str'].iloc[0], x1=df['timestamp_str'].iloc[-1], y0=30, y1=30, line=dict(color="#089981", dash="dash"), row=2, col=1)
        fig.update_yaxes(title_text="RSI (14)", range=[0, 100], row=2, col=1)
        
    # Layout Adjustments for Wide Stretched Chart
    fig.update_layout(
        paper_bgcolor=bg_color, plot_bgcolor=bg_color,
        height=800, margin=dict(l=10, r=10, t=30, b=10),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        title=dict(text=title, font=dict(color=text_color, size=16))
    )
    fig.update_yaxes(side="right", showgrid=True, gridcolor=grid_color, tickfont=dict(color=text_color))
    fig.update_xaxes(showgrid=True, gridcolor=grid_color, tickfont=dict(color=text_color), nticks=12)
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 4. Sidebar Controls & Categorized Assets List
# ---------------------------------------------------------
st.sidebar.header("🕹 Control Panel")
theme_choice = st.sidebar.radio("Theme", ["Dark", "Light"], index=0)
asset_class = st.sidebar.selectbox("Asset Class", ["Crypto", "Forex & Exness", "Metals & Commodities", "NEPSE"])
timeframe = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=2)

show_smc = st.sidebar.checkbox("Show SMC (OB / BOS)", value=True)
show_rsi = st.sidebar.checkbox("Show RSI Indicator", value=True)

# Asset Selection Logic
symbol = ""
yf_symbol = ""

if asset_class == "Crypto":
    crypto_list = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
        "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT", "SUI/USDT"
    ]
    custom_crypto = st.sidebar.text_input("Custom Symbol (उदा: PEPE/USDT, NEAR/USDT)", "")
    if custom_crypto:
        symbol = custom_crypto.upper()
    else:
        symbol = st.sidebar.selectbox("Select Crypto Pair", crypto_list)
    yf_symbol = symbol.replace("/", "-")

elif asset_class == "Forex & Exness":
    forex_list = [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
        "USD/CAD", "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY"
    ]
    custom_forex = st.sidebar.text_input("Custom Forex Pair (उदा: EUR/AUD)", "")
    if custom_forex:
        symbol = custom_forex.upper()
    else:
        symbol = st.sidebar.selectbox("Select Forex Pair", forex_list)
    yf_symbol = symbol.replace("/", "") + "=X"

elif asset_class == "Metals & Commodities":
    metals_map = {
        "Gold (XAU/USD)": "GC=F",
        "Silver (XAG/USD)": "SI=F",
        "Crude Oil (WTI)": "CL=F",
        "Brent Oil": "BZ=F",
        "Natural Gas": "NG=F"
    }
    symbol = st.sidebar.selectbox("Select Commodity", list(metals_map.keys()))
    yf_symbol = metals_map[symbol]

elif asset_class == "NEPSE":
    nepse_symbols = [
        # Commercial Banks
        "NABIL", "NMB", "NICA", "KBL", "GBIME", "EBL", "PCBL", "SANIMA", "SCB", "MBL", "SBL", "PRVU", "ADBL",
        # Hydropower
        "AKPL", "UPPER", "BHPL", "SHPC", "CHCL", "NGPL", "HDPC", "NHPC", "MHCL", "API", "RHPL", "KPCL",
        # Reinsurance & Insurance
        "NRIC", "HRL", "NLIC", "LICN", "NICL", "NIL", "PRIN", "IGI",
        # Microfinance & Others
        "CBBL", "SKBBL", "DDBL", "FMDBL", "NHDL", "NTC", "CIT", "HDL", "CGH", "AHPC"
    ]
    custom_nepse = st.sidebar.text_input("Custom NEPSE Symbol (उदा: STC, NLO)", "")
    if custom_nepse:
        symbol = custom_nepse.upper()
    else:
        symbol = st.sidebar.selectbox("Select NEPSE Stock", nepse_symbols)

# ---------------------------------------------------------
# 5. Data Fetching & Execution
# ---------------------------------------------------------
st.info(f"Loading data for **{symbol}** ({timeframe})...")

try:
    if asset_class == "NEPSE":
        df = generate_nepse_data(symbol)
        df = calculate_indicators(df)
        render_pro_chart(df, f"NEPSE: {symbol}", show_smc, show_rsi, theme_choice)
    else:
        # Fetching 7 days data for clean non-cluttered candles
        data = yf.download(yf_symbol, period="7d", interval=timeframe, progress=False)
        if data.empty:
            st.error(f"Data not found for {symbol}. Check the symbol name.")
        else:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            data = data.reset_index()
            time_col = 'Datetime' if 'Datetime' in data.columns else 'Date'
            data['timestamp_str'] = data[time_col].dt.strftime('%Y-%m-%d %H:%M')
            
            df = calculate_indicators(data)
            render_pro_chart(df, f"{asset_class}: {symbol}", show_smc, show_rsi, theme_choice)
except Exception as e:
    st.error(f"Error fetching chart: {e}")
