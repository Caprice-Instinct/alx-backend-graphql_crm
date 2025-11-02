# CRM Celery Setup

## Prerequisites
1. Install Redis server
2. Install dependencies: `pip install -r requirements.txt`

## Setup Steps
1. Run migrations: `python manage.py migrate`
2. Start Celery worker: `celery -A crm worker -l info`
3. Start Celery Beat: `celery -A crm beat -l info`

## Verification
Check logs in `/tmp/crm_report_log.txt` for weekly CRM reports generated every Monday at 6:00 AM.