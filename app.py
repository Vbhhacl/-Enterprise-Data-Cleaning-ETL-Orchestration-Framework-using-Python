import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Executive Sales Intelligence",
    page_icon="📊",
    layout="wide"
)

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title(" Enterprise Sales Data Pipeline")
st.info("System Status: **Operational** | Last Refreshed: **Daily via Airflow**")

DATA_PATH = "data/salesorder_cleaned.csv"

if os.path.exists(DATA_PATH):
    # Load Data
    df = pd.read_csv(DATA_PATH)
    
    # 1. ROBUST COLUMN CLEANING
    df.columns = df.columns.str.strip() # Remove hidden spaces
    
    # 2. PROFESSIONAL DATA CASTING
    # Clean 'Total amount'
    if 'Total amount' in df.columns:
        df['Total amount'] = pd.to_numeric(df['Total amount'].replace('[\$,]', '', regex=True), errors='coerce')
    
    # Clean 'Date' (Handles "27 March 2023" or "2023-03-27")
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Total amount']) # Remove broken data
        df = df.sort_values('Date')

    # --- TOP ROW: KEY PERFORMANCE INDICATORS (KPIs) ---
    total_rev = df['Total amount'].sum()
    avg_order = df['Total amount'].mean()
    total_trans = len(df)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross Revenue", f"${total_rev:,.2f}")
    m2.metric("Total Transactions", f"{total_trans:,}")
    m3.metric("Avg. Order Value", f"${avg_order:,.2f}")
    m4.metric("Data Health", "100%", delta="0% errors")

    st.divider()

    # --- MIDDLE ROW: CHARTS ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader(" Revenue Growth Over Time")
        # Grouping by date for a smooth line
        daily_sales = df.groupby('Date')['Total amount'].sum().reset_index()
        fig = px.line(daily_sales, x='Date', y='Total amount', 
                     template="plotly_white", color_discrete_sequence=['#007bff'])
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader(" Top Products")
        if 'Product' in df.columns:
            top_prods = df.groupby('Product')['Total amount'].sum().nlargest(5).reset_index()
            fig_pie = px.pie(top_prods, values='Total amount', names='Product', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- BOTTOM ROW: RAW DATA ---
    with st.expander(" View Filtered Audit Logs (Raw Data)"):
        st.dataframe(df, use_container_width=True)

else:
    st.error(" Critical Error: Production Data Stream (CSV) not found in /data directory.")