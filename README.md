# Testing celery in Django App
In this app I'm creating a simple app to test:
1. Create tasks in celery.
2. Schedule tasks with celery-beat.
3. Schedule tasks for a certain date and time to execute.
4. Use Redis as a broker and result backend.
5. Monitor tasks using celery-flower.

## Requirements
```
celery
Django
djangorestframework
flower
redis
django-celery-beat

pytest
pytest-django
```

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
CELERY_BROKER_URL = "redis://127.0.0.1:6379" # you can create a local broker on your server just like your local machine, or you can get a hosting server that provides redis datastore and link to it.
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379" # same as above

# schedule a task to run every minute
CELERY_BEAT_SCHEDULE = {
    "count_model_items": {
        'task': 'tasks.celery_tasks.count_model_items', # you need to define the task before referencing here as you can see in the ```app.task``` section
        'schedule': crontab(minute='*/1'), # for more info about crontab and how to utilize it, visit 'https://crontab.guru/'
    }
}

CELERY_TIMEZONE = 'Asia/Dubai'
```

## Start services
After you have completed the previous steps, start the virtual environment and execute the following commands each one separately to start the services.
```bash
redis-server # to start redis server
celery -A celery_django beat -l info -f celery.log
celery -A celery_django beat -l info -f celery.log 
celery -A celery_django flower --port=5566
```
Use ```-f``` to choose where the log details should be stored.  
For ```flower``` use ```--port``` to choose the port on which flower will be running.  
You can also add ```--detach``` to run celery services as a daemon.

## creating a task
```shared_task``` is the basic way to identify a function as a celery task.
You can create it as below.
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

## another type of tasks
We can also create celery task using the app instance initiated in the first step.
```Python
# This is the app we initiated in the first step
from celery_django.celery import app

@app.task
def count_model_items():
    models_count = SomeModel.objects.all().count()
    count = NumberOfSomeModelItems.objects.create(count=models_count)
    count.save()
    log.info("count: %s", count.count)
    return {"id": count.id, "count": count.count} # The returned value is store in the result backend (in our case ```redis```).
    # You can save lists, sets, hashes and other scalar type values in redis.
```
```app.task``` can be used for few applications. 1 of them being scheduled tasks with celery-beat.
```Python
# schedule a task to run every minute
CELERY_BEAT_SCHEDULE = {
    "count_model_items": {
        'task': 'tasks.celery_tasks.count_model_items', # reference the task you want to schedule
        'schedule': crontab(minute='*/1'), # for more info about crontab and how to utilize it, visit 'https://crontab.guru/'
    }
}
```

Another use case for ```app.task``` is when you want to run a task on a certain date, at a certain time. For that you can call ```apply_async(eta=some_time_in_the_future)```
```Python
task = scheduled_task.apply_async(eta=future)
```
```eta``` should be a datetime instance.

## auto_retry
When your task fails because of any exception, you can let celery ```auto_retry``` the task.
```Python
@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 5})
def count_model_items(self):
    # some code
```
```autoretry_for``` list/tuple of exceptions that triggers retry when raised  
```max_retries``` number of retries before giving up.  
```retry_backoff``` autoretries will be delayed according to the number provided.
to understand more, checkout the [documentation](https://docs.celeryq.dev/en/stable/userguide/tasks.html#Task.autoretry_for)
