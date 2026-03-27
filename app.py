import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="ETL Sales Dashboard", layout="wide")

st.title("🚀 Enterprise Data Pipeline Dashboard")
st.write("This data is automatically cleaned and processed by **Apache Airflow**.")

# 2. Path to your cleaned data
DATA_PATH = "data/salesorder_cleaned.csv"

if os.path.exists(DATA_PATH):
    # Load the data
    df = pd.read_csv(DATA_PATH)
    
    # 3. Key Metrics (KPIs)
    col1, col2, col3 = st.columns(3)
    
    # Metric: Row Count
    col1.metric("Total Transactions", f"{len(df):,}")
    
    # Metric: Total Sales (Using your 'Total amount' column)
    if 'Total amount' in df.columns:
        total_sales = df['Total amount'].sum()
        col2.metric("Total Revenue", f"${total_sales:,.2f}")
    else:
        col2.metric("Total Revenue", "N/A")
        
    col3.metric("Pipeline Status", "Healthy ✅")

    st.divider()

    # 4. Interactive Data Table
    st.subheader("Cleaned Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # 5. Visualizations
    st.subheader("Sales Trends")
    
    if 'Date' in df.columns and 'Total amount' in df.columns:
        # Convert to datetime and sort for the chart
        df['Date'] = pd.to_datetime(df['Date'])
        chart_data = df.groupby('Date')['Total amount'].sum().reset_index().sort_values('Date')
        
        st.line_chart(chart_data.set_index('Date'))
    else:
        st.warning("Could not generate chart. Check 'Date' and 'Total amount' columns.")

else:
    st.error(f"⚠️ Data Source Not Found: Could not find {DATA_PATH}. Please ensure your Airflow DAG has run successfully and you have pushed the CSV to GitHub.")
    st.info("To fix this, run: `git add -f data/salesorder_cleaned.csv && git commit -m 'sync data' && git push` in your terminal.")