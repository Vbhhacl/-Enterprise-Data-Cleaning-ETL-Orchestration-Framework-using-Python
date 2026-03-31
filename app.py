import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Executive Sales Command Center", page_icon="📈", layout="wide")

# --- 2. DATA PIPELINE LOGIC ---
DATA_PATH = "data/salesorder_cleaned.csv"

@st.cache_data(ttl=600)
def load_and_standardize_data(path):
    if not os.path.exists(path):
        return None
    
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    def find_col(targets, df_cols):
        for name in targets:
            for col in df_cols:
                if name.lower() in col.lower(): return col
        return None

    date_key = find_col(['date', 'orderdate'], df.columns)
    amount_key = find_col(['total amount', 'totalvalue', 'totalprice', 'revenue'], df.columns)
    prod_key = find_col(['product', 'item'], df.columns)

    if amount_key:
        df['Total amount'] = pd.to_numeric(df[amount_key].astype(str).replace('[\$,]', '', regex=True), errors='coerce')
    
    if date_key:
        df['Date'] = pd.to_datetime(df[date_key], errors='coerce')
        df['Year'] = df['Date'].dt.year
        df['Month_Year'] = df['Date'].dt.to_period('M').dt.to_timestamp()

    if prod_key:
        df = df.rename(columns={prod_key: 'Product'})

    return df.dropna(subset=['Date', 'Total amount'])

# --- 3. UI RENDERING & ADVANCED ANALYTICS ---
st.title("📈 Executive Sales Command Center")
st.markdown("Automated Enterprise Pipeline | **Status:** 🟢 Operational | **Data Refresh:** Real-time via Airflow")

df = load_and_standardize_data(DATA_PATH)

if df is not None and not df.empty:
    
    # --- SIDEBAR: Global Filters ---
    with st.sidebar:
        st.header("⚙️ Global Filters")
        available_years = sorted(df['Year'].dropna().unique().tolist(), reverse=True)
        selected_years = st.multiselect("Select Year(s):", available_years, default=available_years)
        df_filtered = df[df['Year'].isin(selected_years)] if selected_years else df

    # --- ADVANCED METRICS (MoM Calculations) ---
    # Calculate current and previous period metrics for Deltas
    current_month = df_filtered['Month_Year'].max()
    prev_month = current_month - pd.DateOffset(months=1)

    curr_data = df_filtered[df_filtered['Month_Year'] == current_month]
    prev_data = df_filtered[df_filtered['Month_Year'] == prev_month]

    curr_rev = curr_data['Total amount'].sum()
    prev_rev = prev_data['Total amount'].sum()
    rev_delta = ((curr_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0

    curr_trans = len(curr_data)
    prev_trans = len(prev_data)
    trans_delta = ((curr_trans - prev_trans) / prev_trans * 100) if prev_trans > 0 else 0

    # --- TOP ROW: Contextual KPI Metrics ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(
        label="Gross Revenue (YTD)", 
        value=f"${df_filtered['Total amount'].sum():,.0f}", 
        delta=f"{rev_delta:.1f}% vs Last Month"
    )
    kpi2.metric(
        label="Total Transactions", 
        value=f"{len(df_filtered):,}", 
        delta=f"{trans_delta:.1f}% vs Last Month"
    )
    
    total_revenue = df_filtered['Total amount'].sum()
    total_orders = len(df_filtered)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    kpi3.metric(label="Avg Ticket Size", value=f"${avg_order_value:,.2f}")
    
    top_product = df_filtered.groupby('Product')['Total amount'].sum().idxmax() if 'Product' in df_filtered.columns else "N/A"
    kpi4.metric(label="Top Volume Driver", value=str(top_product))

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABS: Organizing for Depth ---
    tab1, tab2, tab3 = st.tabs(["📊 Revenue Trends", "📦 Product Deep Dive", "🗄️ Raw Data Audit"])

    with tab1:
        st.subheader("Revenue Trajectory & Moving Average")
        monthly_trend = df_filtered.groupby('Month_Year')['Total amount'].sum().reset_index()
        # Add 3-month rolling average for advanced analytics
        monthly_trend['3-Mo Moving Avg'] = monthly_trend['Total amount'].rolling(window=3).mean()

        fig_trend = go.Figure()
        # Base Area Chart
        fig_trend.add_trace(go.Scatter(x=monthly_trend['Month_Year'], y=monthly_trend['Total amount'], 
                                       fill='tozeroy', name='Monthly Revenue', line=dict(color='#2563eb')))
        # Moving Average Line
        fig_trend.add_trace(go.Scatter(x=monthly_trend['Month_Year'], y=monthly_trend['3-Mo Moving Avg'], 
                                       name='3-Mo Trend', line=dict(color='#f59e0b', width=3, dash='dot')))
        
        fig_trend.update_layout(xaxis_title="", yaxis_title="Revenue ($)", margin=dict(l=0, r=0, t=10, b=0), hovermode="x unified")
        st.plotly_chart(fig_trend, use_container_width=True, theme="streamlit")

    with tab2:
        col_bar, col_scatter = st.columns(2)
        with col_bar:
            st.subheader("Revenue by Product")
            product_sales = df_filtered.groupby('Product').agg(
                Revenue=('Total amount', 'sum'),
                Orders=('Total amount', 'count')
            ).reset_index().sort_values('Revenue', ascending=True)
            
            fig_bar = px.bar(product_sales.tail(10), x='Revenue', y='Product', orientation='h', color_discrete_sequence=['#3b82f6'])
            fig_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_bar, use_container_width=True, theme="streamlit")

        with col_scatter:
            st.subheader("Product Performance (Volume vs. Value)")
            # Advanced scatter plot showing which products bring many small orders vs few large orders
            fig_scatter = px.scatter(product_sales, x='Orders', y='Revenue', color='Product', size='Revenue',
                                     hover_name='Product', size_max=40)
            fig_scatter.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
            st.plotly_chart(fig_scatter, use_container_width=True, theme="streamlit")

    with tab3:
        st.subheader("Automated Pipeline Output")
        st.dataframe(df_filtered.sort_values('Date', ascending=False), use_container_width=True)

else:
    st.error("🚨 Critical Error: Data pipeline output not found.")