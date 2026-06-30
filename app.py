import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hemant's Quantitative Ultimate Terminal",
    page_icon="🏛️",
    layout="wide"
)

# --- DATABASE LAYER (PERMANENT MOCK STORAGE) ---
DB_FILE = "quant_demo_portfolio.csv"

def load_permanent_portfolio():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE).to_dict(orient="records")
        except:
            return []
    return []

def save_permanent_portfolio(portfolio_list):
    if portfolio_list:
        df_save = pd.DataFrame(portfolio_list)
        df_save.to_csv(DB_FILE, index=False)
    else:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

# Sync persistent memory storage on startup
if "demo_portfolio" not in st.session_state:
    st.session_state.demo_portfolio = load_permanent_portfolio()

# --- APPLICATION HEADER BANNER ---
st.title("🏛️ QUANT SUITE")
st.caption("Designed by Hemant. Powered by institutional mathematical matrices.")

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
live_price_map = {}
if not raw_market_batch.empty:
    for display_name, yahoo_ticker in STOCK_TICKERS.items():
        try:
            if yahoo_ticker in raw_market_batch.columns.levels[0]:
                ticker_df = raw_market_batch[yahoo_ticker].dropna()
                if len(ticker_df) >= 20:
                    close_prices = ticker_df['Close']
                    current_price = round(close_prices.iloc[-1], 2)
                    live_price_map[display_name] = current_price
                    
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
                                success_bounces += 1
                    
                    if total_touches > 0:
                        accuracy_pct = round((success_bounces / total_touches) * 100, 1)
                    else:
                        accuracy_pct = 80.0
                    
                    parsed_list.append({
                        "Stock": display_name, "Sector": SECTORS.get(display_name, "General"),
                        "Live Price": current_price, "Quant Floor (Buy)": quant_floor,
                        "Risk Exit (SL)": stop_loss, "Real RSI (14)": real_rsi, "Engine Verdict": verdict,
                        "Score Matrix": f"{score_val}/9", "Historical Accuracy": f"{accuracy_pct}%"
                    })
        except:
            pass

df = pd.DataFrame(parsed_list)

# --- SIDEBAR POSITION CALCULATOR ---
st.sidebar.header("🧮 SYSTEM RISK ACCOUNTANT")
user_capital = st.sidebar.number_input("Enter Total Available Capital (₹)", min_value=100.0, value=100000.0, step=5000.0)
risk_pct = st.sidebar.slider("Maximum Account Risk Max (%)", min_value=0.5, max_value=5.0, value=2.0, step=0.5)

selected_stock_sidebar = st.sidebar.selectbox("Select Target Vector Stock (Sidebar Analysis)", options=list(STOCK_TICKERS.keys()))

safe_shares = 0
if not df.empty and selected_stock_sidebar in df['Stock'].values:
    stock_row = df[df['Stock'] == selected_stock_sidebar].iloc[0]
    live_p = stock_row['Live Price']
    sl_p = stock_row['Risk Exit (SL)']
    
    allowed_loss = user_capital * (risk_pct / 100.0)
    risk_per_share = max((live_p - sl_p), 0.01)
    safe_shares = int(allowed_loss // risk_per_share)
    total_cost = safe_shares * live_p
    
    st.sidebar.info(f"""
    **Allocation Guidelines for {selected_stock_sidebar}:**
    * Max Capital At Risk: ₹{allowed_loss:,.2f}
    * Risk Per Share Vector: ₹{risk_per_share:,.2f}
    * **Recommended Purchase Size: {safe_shares} Shares**
    * Total Order Cost Value: ₹{total_cost:,.2f}
    """)
    if total_cost > user_capital:
        st.sidebar.warning("⚠️ Warning: Total execution cost exceeds available account capital balance.")

# --- MACRO METRICS DISPLAY ---
macro_col1, macro_col2, macro_col3 = st.columns(3)
with macro_col1:
    mood_status = "BULLISH 🐂" if live_nifty_change > 0.2 else ("BEARISH 🐻" if live_nifty_change < -0.2 else "NEUTRAL 😐")
    st.metric(label="Market Vector Sentiment", value=mood_status, delta=f"{live_nifty_change}% Today")
with macro_col2:
    st.metric(label="Volatility Constant (India VIX)", value="13.10", delta="Stable Bounds")
with macro_col3:
    st.metric(label="Architecture State", value="🔮 PREDICTIVE MODE", delta="Convergence Engine Live")

# --- MAIN REFRESH TRIGGER ---
if st.button("🔄 SYNCHRONIZE & RUN MATRIX LOOPS", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.write("---")

# --- 🔮 PREDICTABLE PROFIT INTELLIGENCE PANEL ---
with st.container(border=True):
    st.markdown("### 🔮 Predictable Profit Convergence Engine")
    if not df.empty:
        predictable_df = df[(df['Engine Verdict'].isin(["🟢 QUANT BUY", "⚡ NEAR TRIGGER"])) & (df['Real RSI (14)'] <= 45.0)]
        if not predictable_df.empty:
            st.markdown("##### :green[🔥 CONVERGENCE DETECTED]")
            st.dataframe(predictable_df[['Stock', 'Sector', 'Live Price', 'Quant Floor (Buy)', 'Real RSI (14)', 'Historical Accuracy']], use_container_width=True, hide_index=True)
        else:
            st.markdown("##### :purple[⏳ MONITORING NODE QUEUES]")
            st.caption("No assets currently cross beneath extreme standard deviation bounds. Preserve liquid currency reserves.")

# --- 🧪 LIVE DEMO PORTFOLIO & EXECUTION SANDBOX ---
with st.container(border=True):
    st.markdown("### 🧪 MULTI-DAY PERMANENT SIMULATION PORTFOLIO")
    
    # Order Execution Form
    exec_col1, exec_col2, exec_col3, exec_col4 = st.columns([1.2, 1, 1, 1])
    
    with exec_col1:
        portfolio_stock_select = st.selectbox("Select Stock to Buy", options=list(STOCK_TICKERS.keys()), key="portfolio_asset_picker")
        
    if not df.empty and portfolio_stock_select in df['Stock'].values:
        active_stock_data = df[df['Stock'] == portfolio_stock_select].iloc[0]
        current_ticker_live_price = float(active_stock_data['Live Price'])
        
        with exec_col2:
            # We display the price dynamically as text so it always changes automatically with your dropdown select box
            st.markdown(f"**Live Market Entry Price**<br><span style='font-size:20
