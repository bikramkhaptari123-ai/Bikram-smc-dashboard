import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pro Financial & TradingView Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Pro Financial & TradingView Dashboard")

# Sidebar for Asset Selection
st.sidebar.header("⚙️ Settings")
asset_type = st.sidebar.selectbox("Asset Class", ["NEPSE", "Crypto", "Forex", "Commodity"])

if asset_type == "NEPSE":
    nepse_stock = st.sidebar.selectbox("Select NEPSE Stock", ["NABIL", "NMB", "NICA", "KBL", "GBIME", "CIT", "NTC"])
    timeframe = st.sidebar.selectbox("Timeframe", ["1D", "1W", "1M", "6M"], index=0)
    
    # NEPSE Data Generation
    periods_map = {"1D": 120, "1W": 104, "1M": 60, "6M": 24}
    freq_map = {"1D": 'D', "1W": 'W', "1M": 'ME', "6M": 'ME'}
    periods = periods_map.get(timeframe, 120)
    freq = freq_map.get(timeframe, 'D')
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq=freq)
    np.random.seed(hash(nepse_stock) % 2**32)
    base_price = 450 + np.random.randint(50, 500)
    returns = np.random.normal(0.0015, 0.02, size=len(dates))
    price_path = base_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        'open': price_path * (1 + np.random.uniform(-0.008, 0.008, size=len(dates))),
        'high': price_path * (1 + np.random.uniform(0.004, 0.015, size=len(dates))),
        'low': price_path * (1 - np.random.uniform(0.004, 0.015, size=len(dates))),
        'close': price_path,
        'volume': np.random.randint(30000, 500000, size=len(dates))
    }, index=dates)

    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350',
        increasing_fillcolor='#26a69a', decreasing_fillcolor='#ef5350'
    )])
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#131722",
        plot_bgcolor="#131722",
        font=dict(color="#d1d4dc"),
        xaxis_rangeslider_visible=False,
        height=750,
        margin=dict(l=10, r=50, t=30, b=10)
    )
    fig.update_yaxes(side="right", gridcolor="#2a2e39")
    fig.update_xaxes(gridcolor="#2a2e39")
    
    st.subheader(f"📈 NEPSE: {nepse_stock} ({timeframe})")
    st.plotly_chart(fig, use_container_width=True)

else:
    if asset_type == "Crypto":
        symbol = st.sidebar.selectbox("Select Symbol", ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT"])
    elif asset_type == "Forex":
        symbol = st.sidebar.selectbox("Select Symbol", ["FX:EURUSD", "FX:GBPUSD", "FX:USDJPY"])
    else:
        symbol = st.sidebar.selectbox("Select Symbol", ["OANDA:XAUUSD", "TVC:GOLD", "COMEX:GC1!"])

    # Official TradingView Widget for Global Assets
    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:750px;width:100%">
      <div id="tradingview_chart" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "save_image": false,
        "container_id": "tradingview_chart"
      }}
      );
      </script>
    </div>
    """
    st.components.v1.html(tradingview_html, height=760)
