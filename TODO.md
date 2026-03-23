# Airflow DAGs & Monitoring Implementation TODO

## Plan Progress Tracker

✅ **Step 1:** Create TODO.md

✅ **Step 1:** Configure SMTP in airflow.cfg (Gmail app password added)

✅ **Step 1.1:** Backup config/airflow.cfg.backup created

**Pending Steps:**

✅ **Step 2:** Enhance ETL DAG (FileSensor, EmailOperator, retries, logging added)

✅ **Step 3:** Create monitoring DAG (health check + alerts)

3. **Create monitoring DAG (dags/monitoring_dag.py)**  
   - Health checks (success rates, failures)  
   - Email alerts on >5% failure rate (last 7 days)  
   - Summary logging

4. **Update README.md**  
   Document new features, SMTP setup, monitoring.

5. **Restart Airflow services**  
   `docker-compose restart`

6. **Test implementation**  
   - Trigger ETL manually (success path)  
   - Simulate failure & verify email  
   - Check monitoring DAG  
   - Review logs/UI

7. **attempt_completion**

**Instructions:** Update this file after each completed step (mark ✅ and brief note). Use VSCode 'Todo Tree' extension for visualization.


