# Testing celery in Django App
In this app I'm creating a simple app to test:
1. Create tasks in celery.
2. Schedule tasks with celery-beat.
3. Schedule tasks for a certain date and time to execute.
4. Use Redis as a broker and result backend.
5. Monitor tasks using celery-flower.

## Install and initialize

## Config
Create ```celery.py``` in the root project folder and add the following code:
```Python
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "celery_django.settings")
app = Celery("celery_django")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```
and in the ```__init__.py``` add:
```Python
from .celery import app as celery_app

__all__ = ("celery_app",)
```
We are also going to configure the ```broker_url``` and ```result_backend``` in the ```settings.py```:
```Python
CELERY_BROKER_URL = "redis://127.0.0.1:6379"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379"
CELERY_BEAT_SCHEDULE = {
    "count_model_items": {
        'task': 'tasks.celery_tasks.count_model_items',
        'schedule': crontab(minute='*/1'),
    }
}
CELERY_TIMEZONE = 'Asia/Dubai'
```

## shared_task
```Python
from celery import shared_task

@shared_task
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    log.info("Hello from task")
    return True
```
Call the task as a background using:
```Python
task = create_task.delay(int(task_type))
task_id = task.id # to get the id of the task
```
you will receive an **AsyncResult** object that contains the id of the task. 

Using the id you can check the status of the task by calling:
```Python
task_result = AsyncResult(task_id) # to get the task object
task.status # to check the status of the task
task.result # to get the results (if you have configured the CELERY_RESULT_BACKEND)
```

## app.task
```Python
from celery_django.celery import app

@app.task
def count_model_items():
    log.info("Hello World")
    return True
```