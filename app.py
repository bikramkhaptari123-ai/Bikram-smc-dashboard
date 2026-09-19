import streamlit as st

st.set_page_config(page_title="Pro SMC & ICT Trading Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Pro SMC & ICT Ultimate Financial & Trading Dashboard")

# साइडबार सेटिङ्स
st.sidebar.header("⚙️ Market & Asset Settings")
asset_type = st.sidebar.selectbox("Asset Class", ["Crypto", "Forex", "Gold & Commodities", "NEPSE"])

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
        "Polygon (MATIC/USDT)": "BINANCE:MATICUSDT",
        "Shiba Inu (SHIB/USDT)": "BINANCE:SHIBUSDT",
        "Polkadot (DOT/USDT)": "BINANCE:DOTUSDT"
    }
    symbol = crypto_dict[st.sidebar.selectbox("Select Crypto Pair", list(crypto_dict.keys()))]

elif asset_type == "Forex":
    forex_dict = {
        "EUR/USD (Euro / US Dollar)": "FX:EURUSD",
        "GBP/USD (British Pound / US Dollar)": "FX:GBPUSD",
        "USD/JPY (US Dollar / Japanese Yen)": "FX:USDJPY",
        "AUD/USD (Australian Dollar / US Dollar)": "FX:AUDUSD",
        "USD/CAD (US Dollar / Canadian Dollar)": "FX:USDCAD",
        "NZD/USD (New Zealand Dollar / US Dollar)": "FX:NZDUSD",
        "USD/CHF (US Dollar / Swiss Franc)": "FX:USDCHF",
        "EUR/GBP (Euro / British Pound)": "FX:EURGBP",
        "EUR/JPY (Euro / Japanese Yen)": "FX:EURJPY",
        "GBP/JPY (British Pound / Japanese Yen)": "FX:GBPJPY",
        "USD/INR (US Dollar / Indian Rupee)": "FX_IDC:USDINR"
    }
    symbol = forex_dict[st.sidebar.selectbox("Select Forex Pair", list(forex_dict.keys()))]

elif asset_type == "Gold & Commodities":
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
    symbol = comm_dict[st.sidebar.selectbox("Select Commodity", list(comm_dict.keys()))]

else: # NEPSE
    nepse_symbols = [
        "NABIL", "NMB", "NICA", "KBL", "GBIME", "EBL", "PCBL", 
        "SBL", "CZBIL", "SANIMA", "PRVU", "ADBL", "HBL", 
        "AKPL", "UPPER", "BHPL", "NRIC", "HRL", "CIT", "NTC", "NLIC"
    ]
    symbol = f"NEPSE:{st.sidebar.selectbox('Select NEPSE Stock', sorted(nepse_symbols))}"

tv_timeframe = st.sidebar.selectbox("Timeframe", ["1", "5", "15", "30", "60", "240", "D", "W", "M"], index=4, format_func=lambda x: {
    "1": "1m", "5": "5m", "15": "15m", "30": "30m", "60": "1h", "240": "4h", "D": "1 Day", "W": "1 Week", "M": "1 Month"
}[x])

st.info("💡 **SMC & ICT Mode Active**: माथिको TradingView चार्टमा गएर तपाईंले Order Blocks, Fair Value Gaps (FVG), Market Structure Shifts (BOS/CHoCH) सिधै ड्र गर्न वा इन्डिकेटरहरू एड गर्न सक्नुहुन्छ।")

# TradingView Advanced Embed Widget with Full Toolbars & Studies
tradingview_html = f"""
<div class="tradingview-widget-container" style="height:740px;width:100%">
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
    "toolbar_bg": "#1e222d",
    "enable_publishing": false,
    "hide_top_toolbar": false,
    "hide_legend": false,
    "save_image": false,
    "studies": [
      "Volume@tv-basicstudies",
      "MACD@tv-basicstudies",
      "RSI@tv-basicstudies"
    ],
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
st.components.v1.html(tradingview_html, height=760)
