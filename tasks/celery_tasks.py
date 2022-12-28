import time
import logging

from celery import shared_task
from celery_django.celery import app

from .models import SomeModel, NumberOfSomeModelItems

log = logging.getLogger("tasks")

@shared_task
def create_task(task_type):
    time.sleep(int(task_type) * 1)
    log.info("Hello from task")
    return True

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 5})
def count_model_items(self):
    models_count = SomeModel.objects.all().count()
    count = NumberOfSomeModelItems.objects.create(count=models_count)
    count.save()
    log.info("count: %s", count.count)
    return {"id": count.id, "count": count.count}

@app.task
def scheduled_task():
    some = SomeModel.objects.create(name="Scheduled task")
    log.info("some model: %s", some.name)
    return some.id