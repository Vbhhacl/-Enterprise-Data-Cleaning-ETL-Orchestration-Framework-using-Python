from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.standard.operators.email import EmailOperator
from datetime import datetime, timedelta
from airflow.models import DagRun
import logging

def check_dag_health(**context):
    logger = logging.getLogger(__name__)
    
    # Get last 7 days dag runs
    execution_date = context['execution_date']
    start_date = execution_date - timedelta(days=7)
    
    dag_runs = DagRun.find(
        dag_id='my_etl_dag',
        execution_start_date__gte=start_date
    )
    
    total_runs = len(dag_runs)
    if total_runs == 0:
        logger.warning("No DAG runs in last 7 days")
        return
    
    failed_runs = [dr for dr in dag_runs if dr.state == 'failed']
    success_rate = ((total_runs - len(failed_runs)) / total_runs) * 100
    
    logger.info(f"Total runs: {total_runs}, Failed: {len(failed_runs)}, Success rate: {success_rate:.1f}%")
    
    if success_rate < 95:
        context['task_instance'].xcom_push(key='alert_needed', value=True)
        logger.error(f"ALERT: ETL DAG success rate {success_rate:.1f}% below 95% threshold!")
    else:
        logger.info("Health check passed")

default_args = {
    'retries': 2,
}

with DAG(
    dag_id='monitoring_dag',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='0 9 * * 1',  # Weekly Monday 9AM
    catchup=False,
    tags=['monitoring'],
) as dag:

    health_check = PythonOperator(
        task_id='health_check',
        python_callable=check_dag_health
    )

    send_alert = EmailOperator(
        task_id='send_alert',
        to=['vaibhavih2025@gmail.com'],
        subject="ETL DAG Health Alert",
        html_content="""
        <h2>ETL DAG Monitoring Report</h2>
        <p>Last 7 days success rate below 95% threshold.</p>
        <p>Please investigate recent failures in Airflow UI.</p>
        """,
        trigger_rule='all_success'  # Only if alert_needed
    )

    health_check >> send_alert

