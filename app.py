import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Executive Sales Intelligence",
    page_icon="📊",
    layout="wide"
)

# Professional Blue KPI Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] {
        color: #1E3A8A; /* Deep Professional Blue as requested */
        font-size: 32px;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Enterprise Sales Data Pipeline")

DATA_PATH = "data/salesorder_cleaned.csv"

@st.cache_data(ttl=600)
def load_data(path):
    if not os.path.exists(path): return None
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    
    # Standardizing columns
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Month-wise grouping column
        df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    
    if 'Total amount' in df.columns:
        df['Total amount'] = pd.to_numeric(df['Total amount'].replace('[\$,]', '', regex=True), errors='coerce')
    
    return df.dropna(subset=['Date', 'Total amount'])

df = load_data(DATA_PATH)

if df is not None:
    # --- KPI ROW (Now with Professional Blue) ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Gross Revenue", f"${df['Total amount'].sum():,.2f}")
    m2.metric("Total Transactions", f"{len(df):,}")
    m3.metric("Pipeline Status", "Healthy ✅")

    st.divider()

    # --- CHARTS ROW ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Monthly Revenue Growth")
        # CHANGED: Aggregated by Month instead of Daily
        monthly_sales = df.groupby('Month')['Total amount'].sum().reset_index().sort_values('Month')
        fig = px.line(monthly_sales, x='Month', y='Total amount', template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("📦 Product Distribution")
        # RESTORED: Your original Product pie chart logic
        if 'Product' in df.columns:
            top_prods = df.groupby('Product')['Total amount'].sum().nlargest(5).reset_index()
            fig_pie = px.pie(top_prods, values='Total amount', names='Product', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)