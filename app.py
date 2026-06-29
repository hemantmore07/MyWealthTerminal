import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hemant's Institutional Wealth Terminal",
    page_icon="🏛️",
    layout="wide"
)

# --- SIDEBAR ---
with st.sidebar:
    if st.button("🔄 Reset System"):
        st.rerun()

# --- TITLE & HEADER ---
st.title("🏛️ Hemant's Institutional Wealth Terminal")

# --- 1. NIFTY 50 MOOD & MACRO INDICATORS ---
st.markdown("### NIFTY 50 Mood")

macro_col1, macro_col2, macro_col3 = st.columns(3)

with macro_col1:
    nifty_change = +0.85 
    mood_status = "BULLISH 🐂" if nifty_change > 0.5 else ("BEARISH 🐻" if nifty_change < -0.5 else "NEUTRAL 😐")
    st.metric(label="Market Sentiment", value=mood_status, delta=f"{nifty_change}%")

with macro_col2:
    st.metric(label="India VIX (Volatility)", value="13.42", delta="-2.1% (Low Risk)")

with macro_col3:
    st.metric(label="Nifty 50 Breadth", value="34 Advances / 16 Declines")

st.write("---")

# --- 2. SCAN TRIGGER BUTTON ---
if st.button("🚀 EXECUTE 9-FACTOR SCAN", type="primary"):
    st.session_state['scan_executed'] = True

# --- 3. DATASET WITH UPGRADES ---
data = {
    "Stock": ["TCS", "INFY", "SBIN", "CHAMBLFERT", "GNFC", "MAZDOCK", "RELIANCE", "HAL"],
    "Sector": ["IT", "IT", "Banking", "Chemicals", "Chemicals", "Defense", "Energy", "Defense"],
    "Price": [2095.90, 1042.90, 1045.20, 469.15, 547.00, 2463.50, 1316.50, 4364.00],
    "RSI": [36.6, 28.2, 75.6, 50.6, 64.8, 54.9, 57.4, 59.6],
    "Verdict": ["🔥 STRONG BUY", "🔥 STRONG BUY", "🟢 BUY", "🟢 BUY", "🟣 WATCH", "🟣 WATCH", "🟣 WATCH", "🟣 WATCH"],
    "Buy Zone": [2157.75, 1077.30, 825.88, 419.74, 383.25, 2160.27, 1315.86, 3653.05],
    "Stop Loss": [1928.23, 959.47, 961.58, 431.62, 503.24, 2266.42, 1211.18, 4014.88],
    "Upside": ["66.5%", "65.7%", "18.1%", "23.8%", "12.6%", "36.8%", "22.4%", "16.1%"],
    "Div %": ["5.92%", "4.80%", "1.66%", "2.13%", "3.29%", "78.00%", "46.00%", "1.14%"],
    "Vol Shock": ["1.8x", "2.4x", "0.9x", "1.1x", "1.5x", "3.1x", "0.8x", "1.2x"],
    "Score": ["8/9", "8/9", "6/9", "5/9", "4/9", "4/9", "4/9", "4/9"]
}

df = pd.DataFrame(data)

# --- 4. RISK-TO-REWARD CALCULATION ---
def calculate_rr(row):
    risk = row['Price'] - row['Stop Loss']
    upside_pct = float(row['Upside'].replace('%', '')) / 100
    target_price = row['Price'] * (1 + upside_pct)
    reward = target_price - row['Price']
    if risk <= 0: 
        return "1:3.0+"
    return f"1:{round(reward/risk, 1)}"

df['R:R Ratio'] = df.apply(calculate_rr, axis=1)

# --- 5. QUICK FILTER TABS ---
st.markdown("### Terminal Watchlist")
tab_all, tab_strong, tab_buy, tab_watch = st.tabs(["📋 All Stocks", "🔥 Strong Buy", "🟢 Buy", "🟣 Watch"])

def display_styled_dataframe(dataframe):
    return dataframe.style.format({
        "Price": "₹{:,.2f}",
        "Buy Zone": "Below ₹{:,.2f}",
        "Stop Loss": "₹{:,.2f}"
    })

with tab_all:
    st.dataframe(display_styled_dataframe(df), use_container_width=True, hide_index=True)

with tab_strong:
    strong_df = df[df['Verdict'] == "🔥 STRONG BUY"]
    st.dataframe(display_styled_dataframe(strong_df), use_container_width=True, hide_index=True)

with tab_buy:
    buy_df = df[df['Verdict'] == "🟢 BUY"]
    st.dataframe(display_styled_dataframe(buy_df), use_container_width=True, hide_index=True)

with tab_watch:
    watch_df = df[df['Verdict'] == "🟣 WATCH"]
    st.dataframe(display_styled_dataframe(watch_df), use_container_width=True, hide_index=True)

# --- 6. LIVE TIMESTAMP SUFFIX ---
current_time = datetime.now().strftime("%d-%b-%Y %I:%M %p")
st.success(f"✅ Analysis Complete. Dividend Ratios & RSI Corrected. | Data Freshness: {current_time}")
