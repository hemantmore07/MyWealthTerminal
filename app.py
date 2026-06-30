import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hemant's Quantitative Ultimate Terminal",
    page_icon="🏛️",
    layout="wide"
)

# --- PREMIUM APPLE CSS INJECTION ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #000000 !important;
        }
        
        .apple-card {
            background: rgba(22, 22, 23, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }
        
        .apple-title {
            font-size: 32px;
            font-weight: 600;
            letter-spacing: -0.5px;
            color: #f5f5f7;
            margin-bottom: 4px;
        }
        .apple-subtitle {
            font-size: 16px;
            font-weight: 400;
            color: #86868b;
            margin-bottom: 24px;
        }
        
        .badge-green {
            background-color: rgba(52, 199, 89, 0.15);
            color: #30d158;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid rgba(52, 199, 89, 0.3);
            display: inline-block;
        }
        
        .badge-purple {
            background-color: rgba(175, 82, 222, 0.15);
            color: #bf5af2;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid rgba(175, 82, 222, 0.3);
            display: inline-block;
        }
    </style>
""", unsafe_allow_html=True)

# --- APPLE HEADER BANNER ---
st.markdown('<div class="apple-title">🏛️ QUANT SUITE</div>', unsafe_allow_html=True)
st.markdown('<div class="apple-subtitle">Designed by Hemant in California & Mumbai. Powered by institutional mathematical matrices.</div>', unsafe_allow_html=True)

# --- 📖 INTEGRATED TERMINOLOGY GLOSSARY ---
with st.expander("📖 CLICK TO EXPAND: TERMINOLOGY & USAGE GUIDE", expanded=False):
    st.markdown("""
    * **🟢 QUANT BUY:** Signal generated when the asset crosses below its historical statistical floor.
    * **⚡ NEAR TRIGGER:** Price is within 3% of the statistical floor; monitor for immediate action.
    * **🟣 MONITOR:** Asset is cycling within normal, non-advantageous probability ranges.
    * **Quant Floor (Buy):** Derived floor line calculated via a 20-day SMA adjusted by 1.5 standard deviations.
    * **Risk Exit (SL):** Capital safety net. Trigger liquidation if prices fall below this floor.
    * **Real RSI (14):** Mathematical momentum. Values below 30 mean deeply oversold; above 70 means overbought.
    """)

# --- WATCHLIST CONFIG ---
STOCK_TICKERS = {
    "TCS": "TCS.NS", "INFY": "INFY.NS", "LTIM": "LTIM.NS",
    "SBIN": "SBIN.NS", "HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS",
    "ITC": "ITC.NS", "BHARTIARTL": "BHARTIARTL.NS", "M&M": "M&M.NS",
    "LT": "LT.NS", "BEL": "BEL.NS", "HAL": "HAL.NS", "MAZDOCK": "MAZDOCK.NS",
    "RELIANCE": "RELIANCE.NS", "COALINDIA": "COALINDIA.NS"
}

SECTORS = {
    "TCS": "IT", "INFY": "IT", "LTIM": "IT",
    "SBIN": "Banking", "HDFCBANK": "Banking", "ICICIBANK": "Banking",
    "ITC": "FMCG", "BHARTIARTL": "Telecom", "M&M": "Automotive",
    "LT": "Infrastructure", "BEL": "Defense/Tech", "HAL": "Defense", "MAZDOCK": "Defense",
    "RELIANCE": "Energy", "COALINDIA": "Energy"
}

def calculate_rsi(series, periods=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=60)
def execute_advanced_quant_pipeline():
    tickers_list = list(STOCK_TICKERS.values())
    try:
        all_data = yf.download(tickers_list + ["^NSEI"], period="60d", group_by='ticker', progress=False)
        return all_data
    except Exception as e:
        return pd.DataFrame()

with st.spinner("Synchronizing full enterprise mathematical matrices..."):
    raw_market_batch = execute_advanced_quant_pipeline()

live_nifty_change = 0.0
if not raw_market_batch.empty and "^NSEI" in raw_market_batch.columns.levels[0]:
    try:
        nifty_df = raw_market_batch["^NSEI"].dropna()
        if len(nifty_df) >= 2:
            prev_close = nifty_df['Close'].iloc[-2]
            current_price = nifty_df['Close'].iloc[-1]
            live_nifty_change = round(((current_price - prev_close) / prev_close) * 100, 2)
    except:
        pass

parsed_list = []
if not raw_market_batch.empty:
    for display_name, yahoo_ticker in STOCK_TICKERS.items():
        try:
            if yahoo_ticker in raw_market_batch.columns.levels[0]:
                ticker_df = raw_market_batch[yahoo_ticker].dropna()
                if len(ticker_df) >= 20:
                    close_prices = ticker_df['Close']
                    current_price = round(close_prices.iloc[-1], 2)
                    
                    sma_20 = close_prices.iloc[-20:].mean()
                    std_20 = close_prices.iloc[-20:].std()
                    quant_floor = round(sma_20 - (1.5 * std_20), 2)
                    stop_loss = round(quant_floor * 0.95, 2)
                    
                    rsi_series = calculate_rsi(close_prices, 14)
                    real_rsi = round(rsi_series.iloc[-1], 1) if not pd.isna(rsi_series.iloc[-1]) else 50.0
                    
                    score_val = 5
                    if real_rsi < 40: score_val += 1
                    if current_price < sma_20: score_val += 1
                    if real_rsi < 30: score_val += 2
                    
                    if current_price <= quant_floor:
                        verdict = "🟢 QUANT BUY"
                    elif current_price <= (quant_floor * 1.03):
                        verdict = "⚡ NEAR TRIGGER"
                    else:
                        verdict = "🟣 MONITOR"
                    
                    success_bounces = 0
                    total_touches = 0
                    for i in range(20, len(close_prices)-1):
                        hist_window = close_prices.iloc[i-20:i]
                        hist_floor = hist_window.mean() - (1.5 * hist_window.std())
                        if close_prices.iloc[i] <= hist_floor:
                            total_touches += 1
                            future_idx = min(i + 3, len(close_prices)-1)
                            if close_prices.iloc[future_idx] > close_prices.iloc[i]:
