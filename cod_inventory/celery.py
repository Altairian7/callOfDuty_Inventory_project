import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cod_inventory.settings')

app = Celery('cod_inventory')

# Using a string here means the worker doesn't have to serialize :))))
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    'cleanup-expired-sessions': {
        'task': 'inventory.tasks.cleanup_old_sessions',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    'generate-daily-stats': {
        'task': 'inventory.tasks.generate_daily_stats',
        'schedule': crontab(hour=23, minute=55),  # Run daily at 11:55 PM
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')