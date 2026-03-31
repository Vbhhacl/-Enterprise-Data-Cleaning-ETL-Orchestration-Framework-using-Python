import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIGURATION ---
# "wide" layout uses the full screen, essential for BI dashboards
st.set_page_config(page_title="Executive Sales Command Center", page_icon="📈", layout="wide")

# --- 2. DATA PIPELINE LOGIC (Cached & Hardened) ---
DATA_PATH = "data/salesorder_cleaned.csv"

@st.cache_data(ttl=600)  # Cache for 10 minutes to prevent constant reloading
def load_and_standardize_data(path):
    if not os.path.exists(path):
        return None
    
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip() # Clean invisible spaces

    # Fuzzy matching to prevent KeyError if upstream data headers change slightly
    def find_col(targets, df_cols):
        for name in targets:
            for col in df_cols:
                if name.lower() in col.lower():
                    return col
        return None

    date_key = find_col(['date', 'orderdate'], df.columns)
    amount_key = find_col(['total amount', 'totalvalue', 'totalprice', 'revenue'], df.columns)
    prod_key = find_col(['product', 'item'], df.columns)

    # Standardize types
    if amount_key:
        df['Total amount'] = pd.to_numeric(df[amount_key].astype(str).replace('[\$,]', '', regex=True), errors='coerce')
    
    if date_key:
        df['Date'] = pd.to_datetime(df[date_key], errors='coerce')
        df['Year'] = df['Date'].dt.year
        df['Month_Year'] = df['Date'].dt.to_period('M').dt.to_timestamp() # For smooth trendlines

    if prod_key:
        df = df.rename(columns={prod_key: 'Product'})

    # Drop rows where critical data is missing
    return df.dropna(subset=['Date', 'Total amount'])

# --- 3. UI RENDERING ---
st.title("📈 Executive Sales Command Center")
st.markdown("Automated Enterprise Pipeline | **Status:** 🟢 Operational")
st.divider() # Clean visual separation

df = load_and_standardize_data(DATA_PATH)

if df is not None and not df.empty:
    
    # --- SIDEBAR: Global Filters ---
    with st.sidebar:
        st.header("⚙️ Global Filters")
        
        # Year Filter
        available_years = sorted(df['Year'].dropna().unique().tolist(), reverse=True)
        selected_years = st.multiselect("Select Year(s):", available_years, default=available_years)
        
        # Apply filters
        df_filtered = df[df['Year'].isin(selected_years)] if selected_years else df

    # --- TOP ROW: KPI Metrics ---
    # We use Streamlit's native columns and metrics for perfect Dark/Light mode scaling
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_revenue = df_filtered['Total amount'].sum()
    total_orders = len(df_filtered)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    top_product = df_filtered.groupby('Product')['Total amount'].sum().idxmax() if 'Product' in df_filtered.columns else "N/A"

    kpi1.metric(label="Gross Revenue", value=f"${total_revenue:,.0f}")
    kpi2.metric(label="Total Transactions", value=f"{total_orders:,}")
    kpi3.metric(label="Avg Ticket Size", value=f"${avg_order_value:,.2f}")
    kpi4.metric(label="Top Performer (Rev)", value=str(top_product))

    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    # --- MIDDLE ROW: Visualizations ---
    col1, col2 = st.columns([2, 1]) # 2:1 ratio gives the trendline more breathing room

    with col1:
        st.subheader("Monthly Revenue Trend")
        # Aggregate to monthly to eliminate "spaghetti" daily noise
        monthly_trend = df_filtered.groupby('Month_Year')['Total amount'].sum().reset_index()
        
        fig_trend = px.area(
            monthly_trend, 
            x='Month_Year', 
            y='Total amount',
            color_discrete_sequence=['#2563eb'] # Clean, professional blue
        )
        fig_trend.update_layout(xaxis_title="", yaxis_title="Revenue ($)", margin=dict(l=0, r=0, t=10, b=0))
        # theme="streamlit" forces Plotly to respect the user's Dark/Light mode settings natively
        st.plotly_chart(fig_trend, use_container_width=True, theme="streamlit")

    with col2:
        st.subheader("Top Products by Revenue")
        if 'Product' in df_filtered.columns:
            # Horizontal bar charts are superior to pie charts for comparing categorical values
            product_sales = df_filtered.groupby('Product')['Total amount'].sum().reset_index()
            product_sales = product_sales.sort_values('Total amount', ascending=True).tail(10) # Top 10
            
            fig_bar = px.bar(
                product_sales, 
                x='Total amount', 
                y='Product', 
                orientation='h',
                color_discrete_sequence=['#3b82f6']
            )
            fig_bar.update_layout(xaxis_title="", yaxis_title="", margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_bar, use_container_width=True, theme="streamlit")

    # --- BOTTOM ROW: Transparency / Audit ---
    st.divider()
    with st.expander("🔍 Inspect Raw Processed Data"):
        st.markdown("This table displays the validated data directly from the Airflow ETL output. Use this to audit specific transactions.")
        st.dataframe(df_filtered.sort_values('Date', ascending=False), use_container_width=True)

else:
    # Graceful failure state
    st.error("🚨 Critical Error: Data pipeline output not found. Please verify that the Apache Airflow DAG has completed its most recent run.")