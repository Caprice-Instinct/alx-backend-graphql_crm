# CRM Celery Setup

## Setup Steps

1. **Install Redis and dependencies**
   ```bash
   # Install Redis server (varies by OS)
   pip install -r requirements.txt
   ```

2. **Run migrations**
   ```bash
   python manage.py migrate
   ```

3. **Start Celery worker**
   ```bash
   celery -A crm worker -l info
   ```

4. **Start Celery Beat**
   ```bash
   celery -A crm beat -l info
   ```

5. **Verify logs**
   Check logs in `/tmp/crm_report_log.txt` for weekly CRM reports generated every Monday at 6:00 AM.