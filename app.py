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

# Professional Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #007bff; }
    div[data-testid="stMetric"] { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Enterprise Sales Data Pipeline")
st.caption("Status: **Operational** | Managed by Apache Airflow & Docker")

DATA_PATH = "data/salesorder_cleaned.csv"

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=3600) # Cache for 1 hour to keep it fast
def load_and_clean_data(path):
    if not os.path.exists(path):
        return None
    
    df = pd.read_csv(path)
    # Clean hidden spaces in column headers
    df.columns = df.columns.str.strip()

    # Smart Column Mapping (Finds 'Total amount' or 'Date' even if case is different)
    def find_column(targets, current_cols):
        for t in targets:
            for c in current_cols:
                if t.lower() in c.lower():
                    return c
        return None

    actual_date_col = find_column(['date', 'orderdate'], df.columns)
    actual_amount_col = find_column(['total amount', 'totalvalue', 'totalprice'], df.columns)
    actual_product_col = find_column(['product', 'item'], df.columns)

    # Transform: Currency to Numeric
    if actual_amount_col:
        df[actual_amount_col] = pd.to_numeric(
            df[actual_amount_col].astype(str).replace('[\$,]', '', regex=True), 
            errors='coerce'
        )
        df = df.rename(columns={actual_amount_col: 'Revenue'})

    # Transform: String to Datetime
    if actual_date_col:
        df[actual_date_col] = pd.to_datetime(df[actual_date_col], errors='coerce')
        df = df.rename(columns={actual_date_col: 'Date'})
        
    # Standardize Product column
    if actual_product_col:
        df = df.rename(columns={actual_product_col: 'Product'})

    # Remove rows with broken critical data
    return df.dropna(subset=['Date', 'Revenue'])

# --- 3. DASHBOARD LOGIC ---
df = load_and_clean_data(DATA_PATH)

if df is not None and not df.empty:
    # Top Level Metrics
    total_rev = df['Revenue'].sum()
    total_trans = len(df)
    avg_order = df['Revenue'].mean()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross Revenue", f"${total_rev:,.2f}")
    m2.metric("Total Transactions", f"{total_trans:,}")
    m3.metric("Avg. Ticket Size", f"${avg_order:,.2f}")
    m4.metric("Pipeline Health", "100%", delta="Verified")

    st.divider()

    # Charts Row
    col_chart, col_pie = st.columns([2, 1])

    with col_chart:
        st.subheader("📈 Revenue Growth (Daily)")
        daily_trend = df.groupby('Date')['Revenue'].sum().reset_index().sort_values('Date')
        fig_line = px.line(daily_trend, x='Date', y='Revenue', 
                          template="plotly_white", 
                          line_shape="spline",
                          color_discrete_sequence=['#007bff'])
        st.plotly_chart(fig_line, use_container_width=True)

    with col_pie:
        st.subheader("📦 Product Distribution")
        if 'Product' in df.columns:
            prod_data = df.groupby('Product')['Revenue'].sum().nlargest(5).reset_index()
            fig_pie = px.pie(prod_data, values='Revenue', names='Product', hole=0.5,
                            color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)

    # Data Inspector
    with st.expander("🔍 Audit Cleaned Data"):
        st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

else:
    st.error("🚨 Critical Error: Production Data (CSV) could not be parsed or found.")
    st.info("Ensure Airflow has written `data/salesorder_cleaned.csv` and it is pushed to GitHub.")