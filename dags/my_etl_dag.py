from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
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

    # <-- Changed to your email
    sender = "vaibhavih2025@gmail.com"
    receiver = "vaibhavih2025@gmail.com"

   
    password = "ysolicrcwfhznjaq"

    subject = f"Airflow Task Failed: {task_id}"
    body = f"Task: {task_id}\nDAG: {dag_id}\nError: {exception}"

    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.sendmail(sender, receiver, message)

        logging.info(" Email sent successfully")

    except Exception as e:
        logging.error(f" Email failed: {e}")

# 🔹 ETL tasks
def extract():
    logging.info("Starting Extract Task")
    df = pd.read_csv('/opt/airflow/data/employee.csv')
    df = df.head(100)
    df.to_csv('/opt/airflow/data/data.csv', index=False)
    logging.info(" Data Extracted Successfully")

def transform():
    raise Exception("Testing Email Alert ")  
# def transform():
#     logging.info("Starting Transform Task")

#     # Read extracted data
#     df = pd.read_csv('/opt/airflow/data/data.csv')

#     # Remove missing values
#     df = df.dropna()

#     # Modify column (example)
#     if "ExperienceInCurrentDomain" in df.columns:
#         df["ExperienceInCurrentDomain"] = df["ExperienceInCurrentDomain"] * 1.1

#     # Save transformed data
#     df.to_csv('/opt/airflow/data/transformed_data.csv', index=False)

#     logging.info("✅ Data Transformed Successfully")

def load():
    logging.info("Starting Load Task")
    df = pd.read_csv('/opt/airflow/data/transformed_data.csv')
    logging.info(" Data Loaded Successfully")
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
        on_failure_callback=send_failure_email
    )

    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform,
        on_failure_callback=send_failure_email
    )

    load_task = PythonOperator(
        task_id='load',
        python_callable=load,
        on_failure_callback=send_failure_email
    )

    extract_task >> transform_task >> load_task