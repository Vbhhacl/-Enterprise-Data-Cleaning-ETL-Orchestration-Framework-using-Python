from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.standard.operators.email import EmailOperator
from airflow.utils.email import send_email_smtp
from datetime import timedelta
import logging
from datetime import datetime
import pandas as pd

DATA_PATH = "/opt/airflow/data/salesorder.csv"

default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['vaibhavih2025@gmail.com']
}


# -------------------- EXTRACT --------------------
def extract(**context):
    df = pd.read_csv(DATA_PATH, sep="\t")

    print("Raw Rows:", len(df))
    print("Raw Columns:", len(df.columns))

    context["ti"].xcom_push(
        key="raw_data",
        value=df.to_json()
    )


# -------------------- TRANSFORM --------------------
def transform(**context):
    raw_json = context["ti"].xcom_pull(
        task_ids="extract_data",
        key="raw_data"
    )

    df = pd.read_json(raw_json)

    print("Starting Cleaning Process...")

    # 1️⃣ Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # 2️⃣ Remove duplicates
    before_duplicates = len(df)
    df = df.drop_duplicates()
    after_duplicates = len(df)
    print("Duplicates Removed:", before_duplicates - after_duplicates)

    # 3️⃣ Handle missing values
    print("Null values before cleaning:")
    print(df.isnull().sum())

    df = df.dropna()

    # 4️⃣ Enforce correct datatypes
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["profit"] = pd.to_numeric(df["profit"], errors="coerce")
    df["totalprice"] = pd.to_numeric(df["totalprice"], errors="coerce")

    # Remove invalid financial values
    df = df[df["totalprice"] > 0]
    df = df[df["profit"] >= 0]

    # 5️⃣ Feature Engineering
    df["profit_margin"] = (df["profit"] / df["totalprice"]) * 100
    df["order_year"] = df["date"].dt.year
    df["order_month"] = df["date"].dt.month

    print("Final Cleaned Rows:", len(df))
    print("Transformation Completed.")

    context["ti"].xcom_push(
        key="clean_data",
        value=df.to_json()
    )


# -------------------- LOAD --------------------
def load(**context):
    clean_json = context["ti"].xcom_pull(
        task_ids="transform_data",
        key="clean_data"
    )

    df = pd.read_json(clean_json)

    output_path = "/opt/airflow/data/clean_salesorder.csv"
    df.to_csv(output_path, index=False)

    print("Cleaned dataset saved to:", output_path)
    print("Final row count:", len(df))


# -------------------- DAG --------------------
with DAG(
    dag_id="my_etl_dag",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=['etl', 'sales'],
) as dag:

    wait_for_data = FileSensor(
        task_id='wait_for_data',
        filepath=DATA_PATH,
        fs_conn_id='local_filesystem',
        timeout=3600,
        poke_interval=60
    )

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform
    )

    send_failure_email = EmailOperator(
        task_id='send_failure_email',
        to=['vaibhavih2025@gmail.com'],
        subject="ETL Transformation Failed",
        html_content="The transformation task in {{ dag.dag_id }} failed. Please check logs.",
        trigger_rule='one_failed'
    )

    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load
    )

    wait_for_data >> extract_task >> transform_task >> [load_task, send_failure_email]
