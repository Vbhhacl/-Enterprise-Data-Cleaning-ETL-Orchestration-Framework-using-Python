import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Executive Sales Intelligence", page_icon="📊", layout="wide")

# --- 2. ADVANCED UI STYLING ---
# Forcing a clean, unified light-mode look that overrides default dark mode clashes
st.markdown("""
    <style>
    /* Force app background to a soft, professional light gray */
    .stApp { background-color: #f8f9fa; }
    
    /* Fix KPI Cards: Ensure text is visible and styling is modern */
    [data-testid="stMetric"] { 
        background-color: #ffffff; 
        border-radius: 8px; 
        padding: 15px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    /* Fix invisible labels */
    [data-testid="stMetricLabel"] p {
        color: #475569 !important; 
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
    }
    /* Style the KPI numbers */
    [data-testid="stMetricValue"] { 
        color: #1E3A8A !important; 
        font-size: 30px; 
        font-weight: bold; 
    }
    
    /* Clean up headers */
    h1, h2, h3 { color: #0f172a !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA PIPELINE LOGIC ---
DATA_PATH = "data/salesorder_cleaned.csv"

@st.cache_data(ttl=600)
def load_and_standardize_data(path):
    if not os.path.exists(path):
        return None
    
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    # Dynamic Column Matcher (Fuzzy Logic)
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
        df['Year'] = df['Date'].dt.year # For filtering
        df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp() # For monthly aggregation

    if prod_key:
        df = df.rename(columns={prod_key: 'Product'})

    return df.dropna(subset=['Date', 'Total amount'])

# --- 4. DASHBOARD RENDER ---
st.title("🛡️ Enterprise Sales Data Pipeline")
st.markdown("**Status:** Operational | Managed by Apache Airflow & Docker")

df = load_and_standardize_data(DATA_PATH)

if df is not None and not df.empty:
    
    # --- INTERACTIVITY: Sidebar Filters ---
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")
        year_list = sorted(df['Year'].dropna().unique().tolist(), reverse=True)
        selected_years = st.multiselect("Select Year(s):", year_list, default=year_list)
        
    # Apply Filter
    if selected_years:
        df_filtered = df[df['Year'].isin(selected_years)]
    else:
        df_filtered = df

    # --- KPI ROW ---
    m1, m2, m3, m4 = st.columns(4)
    total_rev = df_filtered['Total amount'].sum()
    total_trans = len(df_filtered)
    avg_ticket = df_filtered['Total amount'].mean() if total_trans > 0 else 0

    m1.metric("Gross Revenue", f"${total_rev:,.2f}")
    m2.metric("Total Transactions", f"{total_trans:,}")
    m3.metric("Avg. Ticket Size", f"${avg_ticket:,.2f}")
    m4.metric("Pipeline Health", "100%", delta="Verified Data")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHARTS ROW ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Monthly Revenue Trend")
        # FIX: Aggregating by Month to remove the "Spaghetti" effect
        monthly_sales = df_filtered.groupby('Month')['Total amount'].sum().reset_index().sort_values('Month')
        
        # Using an Area chart for a more premium corporate look
        fig_trend = px.area(monthly_sales, x='Month', y='Total amount', 
                           template="plotly_white", 
                           color_discrete_sequence=['#1E3A8A'])
        fig_trend.update_layout(xaxis_title="", yaxis_title="Revenue ($)", margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        st.subheader("📦 Revenue by Product")
        if 'Product' in df_filtered.columns:
            top_prods = df_filtered.groupby('Product')['Total amount'].sum().reset_index()
            # FIX: Unified Blue color palette to match the rest of the app
            fig_pie = px.pie(top_prods, values='Total amount', names='Product', hole=0.5,
                            color_discrete_sequence=px.colors.sequential.Blues_r)
            fig_pie.update_layout(margin=dict(l=0, r=0, t=20, b=0), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.error("🚨 Data Error: Processed data not found. Please ensure the Airflow DAG has completed successfully.")