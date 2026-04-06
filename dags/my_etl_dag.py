from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import smtplib
import logging

# 🔹 Default args
default_args = {
    'owner': 'vaibhavi', 
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

# 🔹 Email function 
def send_failure_email(context):
    task_instance = context.get('task_instance')
    task_id = task_instance.task_id
    dag_id = task_instance.dag_id
    exception = context.get('exception')

    sender = "vaibhavih2025@gmail.com"
    receiver = "vaibhavih2025@gmail.com"
    
    # 🚨 PRO TIP: Be careful not to show this password on the projector during your 5-min demo!
    password = "ysolicrcwfhznjaq" 
    
    subject = f"Airflow Task Failed: {task_id}"
    body = f"Task: {task_id}\nDAG: {dag_id}\nError: {exception}"
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, message)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Email failed: {e}")

# 🔹 ETL tasks
def extract():
    import pandas as pd # Moved inside to prevent Airflow Scheduler crashes
    logging.info("Starting Extract Task")
    # Read original tab-separated data
    df = pd.read_csv('/opt/airflow/data/salesorder.csv', sep="\t")
    
    # Save as an intermediate extracted CSV to pass to the transform task
    df.to_csv('/opt/airflow/data/salesorder_extracted.csv', index=False)
    logging.info(f"Data Extracted Successfully. Original rows: {len(df)}")

def transform():
    import pandas as pd # Moved inside
    logging.info("Starting Transform Task")
    # Read the extracted data
    df = pd.read_csv('/opt/airflow/data/salesorder_extracted.csv')

    # ---------------- CLEANING ----------------
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Convert date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Remove null dates
    df = df.dropna(subset=["date"])

    # Ensure numeric columns
    df["profit"] = pd.to_numeric(df["profit"], errors="coerce")
    df["totalprice"] = pd.to_numeric(df["totalprice"], errors="coerce")
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")

    # ---------------- NEW COLUMNS ----------------
    # Profit Margin %
    df["profit_margin"] = (df["profit"] / df["totalprice"]) * 100

    # Order Year
    df["order_year"] = df["date"].dt.year

    # Order Month
    df["order_month"] = df["date"].dt.month

    # Save cleaned dataset
    df.to_csv('/opt/airflow/data/salesorder_cleaned.csv', index=False)
    logging.info(f"Data Transformed Successfully. Cleaned rows: {len(df)}")
    
    # to test your email alert again, uncomment the line below
    # raise Exception("Testing Email Alert")

def load():
    import pandas as pd 
    logging.info("Starting Load Task")
    # Load the final cleaned data
    df = pd.read_csv('/opt/airflow/data/salesorder_cleaned.csv')
    
    logging.info("Data Loaded Successfully!")
    logging.info("\n" + str(df.head()))

# 🔹 DAG definition
with DAG(
    dag_id='etl_pipeline_final_email_alert',
    default_args=default_args,
    schedule='@daily',
    catchup=False,
    description='ETL Pipeline with Gmail email alert'
) as dag:

    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract,
        on_failure_callback=send_failure_email # Triggers email ONLY if this fails
    )

    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform,
        on_failure_callback=send_failure_email # Triggers email ONLY if this fails
    )

    load_task = PythonOperator(
        task_id='load',
        python_callable=load,
        on_failure_callback=send_failure_email # Triggers email ONLY if this fails
    )

    # Task Dependencies
    extract_task >> transform_task >> load_task
