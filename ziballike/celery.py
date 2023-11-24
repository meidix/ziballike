import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ziballike.settings')

app = Celery('ziballike')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()

app.conf.beat_schedule = {
    'sumarrize-and-report-to-merchants': {
        'task': 'reports.tasks.sammarize_and_notify',
        'schedule': crontab(minute=0, hour=0)
    }
}

app.conf.task_routes = {
    'reports.tasks.summarize_and_notify': { 'queue': 'reports_queue'},
    'reports.tasks.summarize_and_notify_merchant': { 'queue': 'reports_queue'},
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")