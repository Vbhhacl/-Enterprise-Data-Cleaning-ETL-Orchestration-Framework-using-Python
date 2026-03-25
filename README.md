# Airflow Docker ETL Pipeline

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

### ETL Pipeline (`etl_dag`)
- **Schedule:** Daily (`0 0 * * *`)
- **Tasks:**
  1. **`extract_data`**: Reads `data/salesorder.csv`
  2. **`transform_data`**: Cleans & preprocesses using `data_preprocessing.py`
  3. **`load_data`**: Writes to `data/clean_salesorder.csv`

**Data Flow:**
```
Raw: salesorder.csv ──[extract]──► Pandas DF ──[transform: clean, validate]──► clean_salesorder.csv [load]
```

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
MIT License - feel free to use and modify.

---


