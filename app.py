import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Hemant's Quant Terminal", page_icon="🏛️", layout="wide")

# --- DATABASE LAYER ---
DB_FILE = "quant_demo_portfolio.csv"

def load_permanent_portfolio():
    if os.path.exists(DB_FILE):
        try: return pd.read_csv(DB_FILE).to_dict(orient="records")
        except: return []
    return []

def save_permanent_portfolio(portfolio_list):
    if portfolio_list:
        pd.DataFrame(portfolio_list).to_csv(DB_FILE, index=False)
    elif os.path.exists(DB_FILE):
        os.remove(DB_FILE)

if "demo_portfolio" not in st.session_state:
    st.session_state.demo_portfolio = load_permanent_portfolio()

st.title("🏛️ QUANT SUITE")

# --- WATCHLIST CONFIG ---
STOCK_TICKERS = {
    "TCS": "TCS.NS", "INFY": "INFY.NS", "LTIM": "LTIM.NS",
    "SBIN": "SBIN.NS", "HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS",
    "ITC": "ITC.NS", "BHARTIARTL": "BHARTIARTL.NS", "M&M": "M&M.NS",
    "LT": "LT.NS", "BEL": "BEL.NS", "HAL": "HAL.NS", "MAZDOCK": "MAZDOCK.NS",
    "RELIANCE": "RELIANCE.NS", "COALINDIA": "COALINDIA.NS"
}

def calculate_rsi(series, periods=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=60)
def execute_pipeline():
    return yf.download(list(STOCK_TICKERS.values()), period="60d", group_by='ticker', progress=False)

raw_market_batch = execute_pipeline()

# --- DATA PARSING ---
parsed_list = []
live_price_map = {}
for display_name, yahoo_ticker in STOCK_TICKERS.items():
    if yahoo_ticker in raw_market_batch.columns.levels[0]:
        df_t = raw_market_batch[yahoo_ticker].dropna()
        if len(df_t) > 20:
            price = round(df_t['Close'].iloc[-1], 2)
            live_price_map[display_name] = price
            sma = df_t['Close'].iloc[-20:].mean()
            floor = round(sma - (1.5 * df_t['Close'].iloc[-20:].std()), 2)
            verdict = "🟢 QUANT BUY" if price <= floor else "🟣 MONITOR"
            parsed_list.append({"Stock": display_name, "Live Price": price, "Engine Verdict": verdict})

df = pd.DataFrame(parsed_list)

# --- EXECUTION SANDBOX ---
with st.container(border=True):
    st.markdown("### 🧪 LIVE EXECUTION SANDBOX")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sel_stock = st.selectbox("Select Asset", options=list(STOCK_TICKERS.keys()))
    
    if sel_stock and sel_stock in live_price_map:
        live_p = live_price_map[sel_stock]
        with col2:
            st.markdown(f"**Current Price:** <span style='color:#00ff00;'>₹{live_p:,.2f}</span>", unsafe_allow_html=True)
        with col3:
            qty = st.number_input("Quantity", min_value=1, value=1)
            if st.button("🚀 Add to Portfolio"):
                st.session_state.demo_portfolio.append({
                    "Stock": sel_stock, "Price": live_p, "Qty": qty, 
                    "Total Outlay": live_p * qty, "Date": datetime.now().strftime("%Y-%m-%d")
                })
                save_permanent_portfolio(st.session_state.demo_portfolio)
                st.rerun()

# --- PORTFOLIO LEDGER ---
if st.session_state.demo_portfolio:
    st.markdown("#### 💼 Active Holdings")
    port_df = pd.DataFrame(st.session_state.demo_portfolio)
    st.dataframe(port_df, use_container_width=True)
    if st.button("🗑️ Clear All"):
        st.session_state.demo_portfolio = []
        save_permanent_portfolio([])
        st.rerun()

# --- GRID VIEW ---
st.markdown("### 🖥️ Master Watchlist")
if not df.empty:
    st.dataframe(df, use_container_width=True)
