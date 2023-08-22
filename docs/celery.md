
## Background

We want to upgrade Django from the current version to at least 4. But our current approach to running background tasks, namely `django-background-tasks` is no longer supported in Django 4. Hence, we decided to switch to celery for distributed tasks.


## Developer Notes

### configuration

The celery configuration file is `adhocracy-plus/config/celery.py`.

Currently, we make use of only three config parameters:
- `broker_url = "redis://localhost:6379"`
- `result_backend = "redis"`
- `broker_connection_retry_on_startup = True`

The celery app is configured from the django settings file and namespaced variables. The defaults are defined in `config/settings/base.py` but can be overriden by `config/settings/local.py`.

### tasks

Celery is set up to autodiscover tasks. To register a task import the shared task decorator from celery and apply it to your task function.

```python
from celery import shared_task

@shared_task
def add_two_numbers():
    return 1 + 1
```

For testing purposes we have added a dummy task the prints and returns the string `"hello world"`. The dummy task can be called form the celery CLI via
```
$ celery --app adhocracy-plus call dummy_task
b5351175-335d-4be0-b1fa-06278a613ccf
```



### makefile

We added two makefile commands:

- `celery-worker-start` to start a worker node in the foreground
- `celery-worker-status` to inspect registered tasks, running worker nodes and call the dummy task

