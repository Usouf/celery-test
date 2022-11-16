import time
import logging

from celery import shared_task
from celery_django.celery import app

from .models import SomeModel, NumberOfSomeModelItems

log = logging.getLogger("tasks")

@shared_task
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    log.info("Hello from task")
    return True

@app.task
def count_model_items():
    models_count = SomeModel.objects.all().count()
    log.info("models_count: %s", models_count)
    count = NumberOfSomeModelItems.objects.create(count=models_count)
    count.save()
    log.info("count: %s", count)
    return True

@app.task
def scheduled_task():
    # log.info("scheduled_task: %s", type)
    some = SomeModel.objects.create(name="Scheduled task")
    log.info("some model: %s", some)
    # some.save()