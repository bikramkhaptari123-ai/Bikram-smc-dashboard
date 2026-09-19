import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pro SMC & ICT Trading Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Pro SMC & ICT Financial Dashboard")

st.sidebar.header("⚙️ Dashboard Settings")
asset_type = st.sidebar.selectbox("Asset Class", ["Crypto", "Forex", "Commodity", "NEPSE"])

if asset_type == "NEPSE":
    nepse_symbols = [
        "NABIL", "NMB", "NICA", "KBL", "GBIME", "EBL", "PCBL", 
        "SBL", "CZBIL", "SANIMA", "PRVU", "ADBL", "HBL", 
        "AKPL", "UPPER", "BHPL", "NRIC", "HRL", "CIT", "NTC", "NLIC"
    ]
    nepse_stock = st.sidebar.selectbox("Select NEPSE Stock", sorted(nepse_symbols))
    timeframe = st.sidebar.selectbox("Timeframe", ["1D", "1W", "1M", "6M"], index=0)
    
    periods_map = {"1D": 150, "1W": 104, "1M": 60, "6M": 24}
    freq_map = {"1D": 'D', "1W": 'W', "1M": 'ME', "6M": 'ME'}
    periods = periods_map.get(timeframe, 150)
    freq = freq_map.get(timeframe, 'D')
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq=freq)
    np.random.seed(hash(nepse_stock) % 2**32)
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

    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350',
        increasing_fillcolor='#26a69a', decreasing_fillcolor='#ef5350',
        name="Price"
    )])
    
    shapes = []
    recent_df = df.tail(40)
    for i in range(2, len(recent_df) - 1):
        prev_idx = recent_df.index[i-1]
        if recent_df['close'].iloc[i] > recent_df['open'].iloc[i] and recent_df['close'].iloc[i-1] < recent_df['open'].iloc[i-1]:
            shapes.append(dict(
                type="rect",
                x0=prev_idx, y0=recent_df['low'].iloc[i-1],
                x1=recent_df.index[-1], y1=recent_df['high'].iloc[i-1],
                xref="x", yref="y",
                fillcolor="rgba(38, 166, 154, 0.2)",
                line=dict(color="#26a69a", width=1, dash="dot"),
                layer="below"
            ))
            break

    fig.update_layout(
        shapes=shapes,
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
    
    st.subheader(f"📈 NEPSE SMC Setup: {nepse_stock} ({timeframe})")
    st.plotly_chart(fig, use_container_width=True)

else:
    if asset_type == "Crypto":
        symbol = st.sidebar.selectbox("Select Crypto Symbol", ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT", "BINANCE:BNBUSDT", "BINANCE:XRPUSDT"])
    elif asset_type == "Forex":
        symbol = st.sidebar.selectbox("Select Forex Pair", ["FX:EURUSD", "FX:GBPUSD", "FX:USDJPY", "FX:AUDUSD"])
    else:
        symbol = st.sidebar.selectbox("Select Commodity", ["OANDA:XAUUSD", "TVC:GOLD", "COMEX:GC1!", "COMEX:SI1!"])
    
    tv_timeframe = st.sidebar.selectbox("Timeframe", ["5", "15", "30", "60", "240", "D", "W", "M"], index=5)

    st.info("💡 **SMC & ICT Mode Active**: Use TradingView tools to mark Order Blocks and FVG.")

    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:730px;width:100%">
      <div id="tradingview_chart" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "{tv_timeframe}",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "save_image": false,
        "studies": [
          "MASimple@tv-basicstudies",
          "RSI@tv-basicstudies"
        ],
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    st.components.v1.html(tradingview_html, height=750)
