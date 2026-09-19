import streamlit as st

st.set_page_config(page_title="Pro TradingView Financial Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Pro TradingView Financial Dashboard")

# Sidebar for Asset Selection
st.sidebar.header("⚙️ Settings")
asset_type = st.sidebar.selectbox("Asset Class", ["NEPSE", "Crypto", "Forex", "Commodity"])

if asset_type == "NEPSE":
    nepse_stock = st.sidebar.selectbox("Select NEPSE Stock", ["NABIL", "NMB", "NICA", "KBL", "GBIME", "CIT", "NTC"])
    # TradingView par NEPSE stocks mate general exchange format use thay che
    symbol = f"NEPSE:{nepse_stock}"
elif asset_type == "Crypto":
    symbol = st.sidebar.selectbox("Select Symbol", ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT"])
elif asset_type == "Forex":
    symbol = st.sidebar.selectbox("Select Symbol", ["FX:EURUSD", "FX:GBPUSD", "FX:USDJPY"])
else:
    symbol = st.sidebar.selectbox("Select Symbol", ["OANDA:XAUUSD", "TVC:GOLD", "COMEX:GC1!"])

# Embedding TradingView Advanced Real-Time Widget with NEPSE support
tradingview_html = f"""
<!-- TradingView Widget BEGIN -->
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
<!-- TradingView Widget END -->
"""

st.components.v1.html(tradingview_html, height=760)
