# adhocracy+

[adhocracy.plus](https://adhocracy.plus/) is a free Open-Source participation platform maintained and primarily developed by Liquid Democracy e.V.. It is based on [adhocracy 4](https://github.com/liqd/adhocracy4) and [Django](https://github.com/django/django).

![Build Status](https://github.com/liqd/adhocracy-plus/actions/workflows/django.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/liqd/adhocracy-plus/badge.svg?branch=main)](https://coveralls.io/github/liqd/adhocracy-plus?branch=main)

## Getting started

adhocracy+ is designed to make online participation easy and accessible to everyone. It can be used on our SaaS-platform or installed on your own servers. How to get started on our platform is explained [here](https://adhocracy.plus/info/start/).

## Installation for development

### Requirements

 * nodejs (+ npm)
 * python 3.x (+ venv + pip)
 * libpq (only if postgres should be used)
 * sqlite3 [with JSON1 enabled](https://code.djangoproject.com/wiki/JSON1Extension)
 * redis (in production, not needed for development)

### Installation

    git clone https://github.com/liqd/adhocracy-plus.git
    cd adhocracy-plus
    make install
    make fixtures

### Start virtual environment

    source venv/bin/activate

### Check if tests work

    make test

### Start a local server

    make watch

### Use postgresql database for testing

run the following command once:
```
make postgres-create
```
to start the test server with postgresql, run:
```
export DATABASE=postgresql
make postgres-start
make watch
```

Go to http://localhost:8004/ and login with admin@liqd.net | password

### Use Celery for task queues

For a celery worker to pick up tasks you need to make sure that:
- the redis server is running
- the celery config parameter "always eager" is disabled (add `CELERY_TASK_ALWAYS_EAGER = False` to your `local.py`)

To start a celery worker node in the foreground, call:
```
make celery-worker-start
```

To inspect all registered tasks, list the running worker nodes, call:
```
make celery-worker-status
```

To send a dummy task to the queue and report the result, call:
```
make celery-worker-dummy-task
```

## Installation on a production system

You like adhocracy+ and want to run your own version? An installation guide for production systems can be found [here](./docs/installation_prod.md).

## Contributing or maintaining your own fork

If you found an issue, want to contribute, or would like to add your own features to your own version of adhocracy+, check out [contributing](./docs/contributing.md).

## Security

We care about security. So, if you find any issues concerning security, please send us an email at info [at] liqd [dot] net.
