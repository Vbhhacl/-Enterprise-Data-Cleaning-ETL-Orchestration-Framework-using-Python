import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ETL Sales Dashboard", layout="wide")

st.title("🚀 Enterprise Data Pipeline Dashboard")

DATA_PATH = "data/salesorder_cleaned.csv"

if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    
    # --- CRITICAL DATA CLEANING ---
    # 1. Clean 'Total amount': Remove '$' and ',' then convert to numeric
    if 'Total amount' in df.columns:
        df['Total amount'] = df['Total amount'].replace('[\$,]', '', regex=True).astype(float)
    
    # 2. Clean 'Date': Convert to actual datetime objects
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']) # Remove any rows with broken dates
    # ------------------------------

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", f"{len(df):,}")
    
    if 'Total amount' in df.columns:
        total_sales = df['Total amount'].sum()
        col2.metric("Total Revenue", f"${total_sales:,.2f}")
    
    col3.metric("Pipeline Status", "Healthy ✅")

    st.subheader("Sales Trends")
    if not df.empty:
        chart_data = df.groupby('Date')['Total amount'].sum().sort_index()
        st.line_chart(chart_data)

    st.subheader("Data Preview")
    st.dataframe(df.head(10))

else:
    st.error("Data file not found.")
    