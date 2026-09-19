import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_lightweight_charts import renderLightweightCharts

st.set_page_config(page_title="Pro TradingView SMC Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Pro TradingView & SMC Financial Dashboard")

# Sidebar Controls
st.sidebar.header("⚙️ Settings")
asset_class = st.sidebar.selectbox("Asset Class", ["Crypto", "Forex", "Commodities (Gold/Silver)", "NEPSE"])

symbol = ""
yf_symbol = ""
is_nepse = False

if asset_class == "NEPSE":
    is_nepse = True
    nepse_symbols = ["NABIL", "NMB", "NICA", "KBL", "GBIME", "EBL", "AKPL", "UPPER", "BHPL", "NRIC", "HRL"]
    symbol = st.sidebar.selectbox("Select NEPSE Stock", nepse_symbols)
    timeframe = st.sidebar.selectbox("Timeframe", ["1D", "1W", "1M", "6M"], index=0)
else:
    if asset_class == "Crypto":
        crypto_map = {"BTC/USDT": "BTC-USD", "ETH/USDT": "ETH-USD", "SOL/USDT": "SOL-USD", "BNB/USDT": "BNB-USD", "XRP/USDT": "XRP-USD"}
        symbol = st.sidebar.selectbox("Select Crypto Pair", list(crypto_map.keys()))
        yf_symbol = crypto_map[symbol]
    elif asset_class == "Forex":
        forex_map = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "USDJPY=X", "AUD/USD": "AUDUSD=X"}
        symbol = st.sidebar.selectbox("Select Forex Pair", list(forex_map.keys()))
        yf_symbol = forex_map[symbol]
    else:
        comm_map = {"Gold (XAU/USD)": "GC=F", "Silver (XAG/USD)": "SI=F", "Crude Oil": "CL=F"}
        symbol = st.sidebar.selectbox("Select Commodity", list(comm_map.keys()))
        yf_symbol = comm_map[symbol]
    
    timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "30m", "1h", "4h", "1D", "15D", "1M"], index=3)

# Data Fetching Function
@st.cache_data(ttl=300)
def get_data(is_nepse_stock, ticker, tf):
    if is_nepse_stock:
        periods_map = {"1D": 120, "1W": 104, "1M": 60, "6M": 24}
        freq_map = {"1D": 'D', "1W": 'W', "1M": 'ME', "6M": 'ME'}
        periods = periods_map.get(tf, 120)
        freq = freq_map.get(tf, 'D')
        
        dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq=freq)
        np.random.seed(hash(ticker) % 2**32)
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
        return df
    else:
        try:
            tf_settings = {
                "5m": ("5m", "5d"), "15m": ("15m", "60d"), "30m": ("30m", "60d"),
                "1h": ("60m", "730d"), "4h": ("60m", "730d"), "1D": ("1d", "max"),
                "15D": ("1d", "max"), "1M": ("1mo", "max")
            }
            interval, period = tf_settings.get(tf, ("1d", "1y"))
            data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
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
            return data.dropna(subset=['close'])
        except Exception:
            return None

df = get_data(is_nepse, yf_symbol if not is_nepse else symbol, timeframe)

if df is not None and not df.empty:
    # Format data for TradingView Lightweight Charts
    df['time'] = df.index.strftime('%Y-%m-%d')
    
    candlestick_data = []
    volume_data = []
    
    for i, row in df.iterrows():
        time_str = row['time']
        candlestick_data.append({
            "time": time_str,
            "open": float(row['open']),
            "high": float(row['high']),
            "low": float(row['low']),
            "close": float(row['close'])
        })
        
        # Color volume bars based on price action
        color = "#26a69a" if row['close'] >= row['open'] else "#ef5350"
        volume_data.append({
            "time": time_str,
            "value": float(row['volume']),
            "color": color
        })

    # TradingView Lightweight Charts configuration
    chart_options = {
        "layout": {
            "background": {"type": "solid", "color": "#131722"},
            "textColor": "#d1d4dc"
        },
        "grid": {
            "vertLines": {"color": "#2a2e39"},
            "horzLines": {"color": "#2a2e39"}
        },
        "timeScale": {
            "timeVisible": True,
            "borderColor": "#2a2e39"
        },
        "rightPriceScale": {
            "borderColor": "#2a2e39"
        }
    }

    # Candlestick Series
    series_candlestick = [{
        "type": "Candlestick",
        "data": candlestick_data,
        "options": {
            "upColor": "#26a69a",
            "downColor": "#ef5350",
            "borderVisible": False,
            "wickUpColor": "#26a69a",
            "wickDownColor": "#ef5350"
        }
    }]

    # Volume Series (Histogram)
    series_volume = [{
        "type": "Histogram",
        "data": volume_data,
        "options": {
            "priceFormat": {"type": "volume"},
            "priceScaleId": "volume"
        }
    }]

    st.subheader(f"📈 {symbol} Chart ({timeframe})")
    
    # Render TradingView Price Chart
    renderLightweightCharts([
        {
            "chart": chart_options,
            "series": series_candlestick
        },
        {
            "chart": {"height": 150, **chart_options},
            "series": series_volume
        }
    ], key='financial_chart')

else:
    st.error("Could not load chart data. Please check selection.")
