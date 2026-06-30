import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Quant Terminal", layout="wide")

# --- STORAGE ---
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

# --- CORE LOGIC ---
STOCK_TICKERS = {"TCS": "TCS.NS", "INFY": "INFY.NS", "SBIN": "SBIN.NS"} # Expand this list as needed

@st.cache_data(ttl=60)
def get_data():
    return yf.download(list(STOCK_TICKERS.values()), period="60d", group_by='ticker', progress=False)

raw_data = get_data()

parsed_data = []
for name, ticker in STOCK_TICKERS.items():
    if ticker in raw_data.columns.levels[0]:
        df_t = raw_data[ticker].dropna()
        if len(df_t) > 20:
            price = round(df_t['Close'].iloc[-1], 2)
            # Simple logic for Demo
            parsed_data.append({"Stock": name, "Live Price": price, "Engine Verdict": "🟢 QUANT BUY" if price < 3000 else "🟣 MONITOR"})

df = pd.DataFrame(parsed_data)

# --- PORTFOLIO SECTION (FIXED SYNTAX) ---
with st.container(border=True):
    st.markdown("### 🧪 MULTI-DAY PERMANENT SIMULATION PORTFOLIO")
    
    col1, col2 = st.columns(2)
    with col1:
        sel_stock = st.selectbox("Select Asset", options=df['Stock'].tolist() if not df.empty else [])
    
    if not df.empty and sel_stock:
        curr_price = df[df['Stock'] == sel_stock]['Live Price'].iloc[0]
        # FIXED: Proper f-string closure and syntax
        st.markdown(f"**Live Market Entry Price**: <span style='color:green; font-size:20px;'>₹{curr_price}</span>", unsafe_allow_html=True)
        
        qty = st.number_input("Order Quantity", min_value=1, value=1)
        
        if st.button("🚀 Add to Portfolio"):
            st.session_state.demo_portfolio.append({
                "Stock": sel_stock, 
                "Price": curr_price, 
                "Qty": qty, 
                "Date": datetime.now().strftime("%Y-%m-%d")
            })
            save_permanent_portfolio(st.session_state.demo_portfolio)
            st.rerun()

# --- GRID VIEW (FIXED KEYERROR) ---
st.markdown("### 🖥️ Global System Watchlist")
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("Loading matrix...")
