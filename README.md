# Airflow Docker ETL Pipeline ✅

## Project Milestones (Completed 8-Week Development)

✅ **Milestone 1: Weeks 1–2 Environment Setup & Pipeline Design**  
Configured Airflow Docker environment (`docker-compose.yaml`, `config/airflow.cfg`), defined ETL architecture, set up extraction scripts in `dags/`.

✅ **Milestone 2: Weeks 3–4 Data Cleaning & Transformation**  
Implemented pandas-based cleaning rules in `data_preprocessing.py`, transformations for salesorder.csv → clean_salesorder.csv, pipeline testing via multiple DAG runs.

✅ **Milestone 3: Weeks 5–6 Orchestration & Monitoring**  
Added Airflow DAGs (`my_etl_dag.py`, `monitoring_dag.py`) with scheduling, logging (`logs/`), Gmail alerts (EmailOperator).

✅ **Milestone 4: Weeks 7–8 Dashboards & Deployment**  
Integrated dashboard framework (Streamlit/Dash ready), tested on production-scale datasets, finalized deployable framework.

## Overview

This project provides a complete, Dockerized Apache Airflow environment for orchestrating ETL (Extract, Transform, Load) workflows on sales order data. It features a production-ready setup with persistent volumes for DAGs, logs, data, and Airflow metadata.

**Key Features:**
  - Fully containerized Airflow stack (webserver, scheduler, worker)
  - Custom ETL DAGs for sales order data processing
  - Persistent PostgreSQL metadata database
  - Sample data pipeline: `salesorder.csv` → `clean_salesorder.csv`
  - Scheduled and manual DAG execution with historical logs
  - Configurable via `docker-compose.yaml` and `airflow.cfg`

## Project Structure

```
airflow-docker/
├── docker-compose.yaml          # Docker Compose configuration
├── config/
│   └── airflow.cfg             # Airflow configuration
├── dags/                       # Airflow DAGs (Python files)
│   ├── my_etl_dag.py          # Main ETL DAG
│   └── data_preprocessing.py   # Data preprocessing utilities
├── data/                       # Input/output data files
│   ├── salesorder.csv         # Raw sales order data (input)
│   └── clean_salesorder.csv   # Processed sales order data (output)
├── logs/                       # Airflow logs (persistent)
│   ├── dag_id=etl/            # Legacy ETL DAG logs
│   └── dag_id=etl_dag/        # Current ETL DAG logs
├── plugins/                    # Custom Airflow plugins (if needed)
└── README.md                  # This file
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Local Data    │    │   Airflow UI     │    │  PostgreSQL DB  │
│  (salesorder.csv)│◄──►│ (localhost:8080) │◄──►│ (Metadata/Log) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                         ┌────▼────┐
                         │  DAGs   │  extract_data ──► transform_data ──► load_data
                         │ (dags/) │
                         └──────────┘
                              │
                         ┌────▼────┐
                         │  Logs   │ (persistent volume)
                         └──────────┘
```

## Prerequisites

- Docker & Docker Compose
- 4GB+ RAM (recommended for Airflow + Postgres)
- Windows 11 / Linux / macOS

## Quick Start

1. **Clone/Navigate to project:**
   ```bash
   cd c:/Users/ADMIN/airflow-docker
   ```

2. **Start the stack:**
   ```bash
   docker-compose up -d
   ```

3. **Initialize Airflow database (first run only):**
   ```bash
   docker-compose exec airflow-worker airflow db init
   ```

4. **Create Airflow admin user:**
   ```bash
   docker-compose exec airflow-worker airflow users create \
     --username admin \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com \
     --password admin
   ```

5. **Access Airflow UI:**
   Open [http://localhost:8080](http://localhost:8080) (admin/admin)

6. **Enable & Trigger DAGs:**
   - Navigate to `etl_dag` in UI
   - Toggle ON and trigger manually or wait for schedule

## DAG Details

### Enhanced ETL Pipeline (`my_etl_dag`)
- **Schedule:** Daily (`@daily`)
- **Tasks:**
  1. **`wait_for_data`**: FileSensor waits for `salesorder.csv`
  2. **`extract_data`**: Reads raw CSV (retries=3)
  3. **`transform_data`**: Cleans/normalizes data (retries=3, structured logging)
  4. **`load_data`**: Writes cleaned CSV
  5. **`send_failure_email`**: Gmail alert on transform failure

**Features Added:**
  - Retry logic with 5min delay
  - Gmail notifications (SMTP configured)
  - File existence check
  - Structured logging
  - Tags: ['etl', 'sales']

**Data Flow:**
```
salesorder.csv ──[wait]──[extract]──► [transform] ──► clean_salesorder.csv [load]
                              ↓ (fail)
                         Email Alert

### Monitoring DAG (`monitoring_dag`)
- **Schedule:** Weekly (Monday 9AM)
- **Tasks:**
  1. **`health_check`**: Calculates ETL success rate (last 7 days)
  2. **`send_alert`**: Email if success rate <95%

**Alert Threshold:** >5% failure rate triggers Gmail notification

### Customization
Edit DAGs in `dags/` and restart scheduler:
```bash
docker-compose restart airflow-scheduler
```

## Volumes & Persistence

| Service     | Volume Path              | Purpose                  |
|-------------|--------------------------|--------------------------|
| `postgres`  | `./postgres-data/`       | Metadata database        |
| `airflow`   | `./logs/`                | Task/DAG logs            |
| `dags`      | `./dags/`                | DAG Python files         |
| `data`      | `./data/`                | Input/output datasets    |

## Commands

### Useful Docker Commands
```bash
# View logs
docker-compose logs -f

# Airflow CLI (via worker container)
docker-compose exec airflow-worker airflow dags list
docker-compose exec airflow-worker airflow dags test etl_dag 2026-03-22

# Stop/Reset
docker-compose down -v  # Removes volumes (data loss!)
docker-compose down     # Keeps volumes
```

### Testing DAG
```bash
docker-compose exec airflow-worker airflow dags test etl_dag $(date -Iseconds --date='1 days ago')
```

## Configuration

- **Airflow Settings:** `config/airflow.cfg`
- **Executor:** CeleryExecutor (scalable)
- **Ports:**
  - Airflow UI: `8080`
  - Flower (Celery): `5555`
  - Postgres: `5432`

## Troubleshooting

| Issue                          | Solution |
|--------------------------------|----------|
| `DAG not visible`              | Check `dags/` permissions, restart scheduler |
| `DB Init failed`               | `docker-compose down -v && docker-compose up -d` |
| `Out of Memory`                | Increase Docker RAM limit |
| `Tasks failing`                | Check `./logs/dag_id=etl_dag/` |
| `CSV not found`                | Verify `data/salesorder.csv` exists |

**Log Locations:**
```
./logs/dag_id=etl_dag/[run_id]/[task_id]/
```

## Extending the Pipeline

1. **Add new DAG:**
   ```
   dags/my_new_dag.py
   ```

2. **New data source:**
   ```
   data/new_source.csv
   ```

3. **Custom operators:** Place in `plugins/`

## Production Considerations

  - **Secrets:** Use Airflow Variables/Connections
  - **Monitoring:** Enable Flower (`docker-compose up flower`)
  - **Scaling:** Increase `worker_count` in `docker-compose.yaml`
  - **Backup:** Regularly backup `./postgres-data/` and `./logs/`

## License
See [licence.txt](licence.txt) (MIT License)

*Production-ready 8-week ETL framework built for sales order workflows.*

