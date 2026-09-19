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

st.title("📊 Pro SMC & ICT Financial & Trading Dashboard")

# Sidebar for Asset Selection & Timeframes
st.sidebar.header("⚙️ Advanced Dashboard Settings")
asset_type = st.sidebar.selectbox("Asset Class", ["Crypto", "Forex", "Commodity", "NEPSE"])

if asset_type == "Crypto":
    crypto_dict = {
        "Bitcoin (BTC/USDT)": "BINANCE:BTCUSDT",
        "Ethereum (ETH/USDT)": "BINANCE:ETHUSDT",
        "Solana (SOL/USDT)": "BINANCE:SOLUSDT",
        "Binance Coin (BNB/USDT)": "BINANCE:BNBUSDT",
        "Ripple (XRP/USDT)": "BINANCE:XRPUSDT",
        "Cardano (ADA/USDT)": "BINANCE:ADAUSDT",
        "Dogecoin (DOGE/USDT)": "BINANCE:DOGEUSDT",
        "Avalanche (AVAX/USDT)": "BINANCE:AVAXUSDT",
        "Chainlink (LINK/USDT)": "BINANCE:LINKUSDT",
        "Polygon (MATIC/USDT)": "BINANCE:MATICUSDT"
    }
    selected_name = st.sidebar.selectbox("Select Crypto Pair", list(crypto_dict.keys()))
    symbol = crypto_dict[selected_name]

elif asset_type == "Forex":
    forex_dict = {
        "EUR/USD (Euro / US Dollar)": "FX:EURUSD",
        "GBP/USD (British Pound / US Dollar)": "FX:GBPUSD",
        "USD/JPY (US Dollar / Japanese Yen)": "FX:USDJPY",
        "AUD/USD (Australian Dollar / US Dollar)": "FX:AUDUSD",
        "USD/CAD (US Dollar / Canadian Dollar)": "FX:USDCAD",
        "NZD/USD (New Zealand Dollar / US Dollar)": "FX:NZDUSD",
        "USD/CHF (US Dollar / Swiss Franc)": "FX:USDCHF",
        "EUR/GBP (Euro / British Pound)": "EURGBP",
        "EUR/JPY (Euro / Japanese Yen)": "EURJPY",
        "GBP/JPY (British Pound / Japanese Yen)": "GBPJPY"
    }
    selected_name = st.sidebar.selectbox("Select Forex Pair", list(forex_dict.keys()))
    symbol = forex_dict[selected_name]

elif asset_type == "Commodity":
    comm_dict = {
        "Gold Spot (XAU/USD)": "OANDA:XAUUSD",
        "Gold Futures": "COMEX:GC1!",
        "Silver Spot (XAG/USD)": "OANDA:XAGUSD",
        "Silver Futures": "COMEX:SI1!",
        "Crude Oil WTI": "NYMEX:CL1!",
        "Brent Crude Oil": "TVC:UKOUSD",
        "Natural Gas": "NYMEX:NG1!",
        "Copper Futures": "COMEX:HG1!"
    }
    selected_name = st.sidebar.selectbox("Select Commodity", list(comm_dict.keys()))
    symbol = comm_dict[selected_name]

else: # NEPSE
    nepse_symbols = [
        "NABIL", "NMB", "NICA", "KBL", "GBIME", "EBL", "PCBL", 
        "SBL", "CZBIL", "SANIMA", "PRVU", "ADBL", "HBL", 
        "AKPL", "UPPER", "BHPL", "NRIC", "HRL", "CIT", "NTC", "NLIC"
    ]
    nepse_stock = st.sidebar.selectbox("Select NEPSE Stock", sorted(nepse_symbols))
    symbol = f"NEPSE:{nepse_stock}"

tv_timeframe = st.sidebar.selectbox("Timeframe", ["1", "5", "15", "30", "60", "240", "D", "W", "M"], index=4, format_func=lambda x: {
    "1": "1m", "5": "5m", "15": "15m", "30": "30m", "60": "1h", "240": "4h", "D": "1 Day", "W": "1 Week", "M": "1 Month"
}[x])

# ICT & SMC Quick Guide & Indicator Control Panel
st.markdown("""
    <div style="background-color: #1e222d; padding: 10px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid #2962ff;">
        <strong>🎯 ICT & SMC Strategy Center:</strong> Use the TradingView toolbar above the chart to find <b>Order Blocks (OB)</b>, <b>Fair Value Gaps (FVG)</b>, <b>Market Structure Shift (MSS)</b>, and <b>Liquidity Pools (Equal Highs/Lows)</b>.
    </div>
""", unsafe_allow_html=True)

# Advanced TradingView Widget with Built-in SMC/ICT Toolkit Support
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
      "RSI@tv-basicstudies",
      "MACD@tv-basicstudies"
    ],
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
st.components.v1.html(tradingview_html, height=750)
