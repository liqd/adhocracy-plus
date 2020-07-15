# adhocracy+

[adhocracy.plus](https://adhocracy.plus/) is a free Open-Source participation platform maintained and primarily developed by Liquid Democracy e.V.. It is based on [adhocracy 4](https://github.com/liqd/adhocracy4) and [Django](https://github.com/django/django).

[![Build Status](https://travis-ci.org/liqd/a4-product.svg?branch=master)](https://travis-ci.org/liqd/a4-product)
[![Coverage Status](https://coveralls.io/repos/github/liqd/adhocracy-plus/badge.svg?branch=master)](https://coveralls.io/github/liqd/adhocracy-plus?branch=master)

## Getting started

adhocracy+ is designed to make online participation easy and accessible to everyone. It can be used on our SaaS-platform or installed on your own servers. How to get started on our platform is explained [here](https://adhocracy.plus/info/start/).

### Installation for development

Requirements:
*   nodejs (+ npm)
*   python 3.x (+ venv + pip)
*   libmagic
*   libjpeg
*   libpq (only if postgres should be used)

Installation:

    git clone https://github.com/liqd/adhocracy-plus.git
    cd adhocracy-plus
    make install
    make fixtures

Check if it works:

    make test

Check it out:

    make watch

Go to http://localhost:8004/ and login with admin@liqd.net | password

### Installation for production

#### Requirements:
 * python3
 * python3-dev
 * python3-pip
 * virtualenvwrapper
 * build-essential
 * nodejs

#### Setup

Create and switch to user (as `root` or using `sudo`):
```
adduser aplus
su aplus
cd
```

Get the code:
```
git clone https://github.com/liqd/adhocracy-plus.git
cd adhocracy-plus
git checkout release
```

Create and launch virtual environment:
```
mkvirtualenv aplus
```

Install and build:
```
npm install
npm run build:prod
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.build
python manage.py compilemessages
python manage.py collectstatic
```

Add config in `local.py`:
```
~/aplus/adhocracy-plus/config/settings/local.py

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'aplus',
  }
}
MEDIA_ROOT='/home/aplus/aplus-media'
SECRET_KEY = u'SOMESECRETKEY'

ALLOWED_HOSTS = [u'example.com', u'localhost']
```

Populate Database:
```
python manage.py migrate
```

Try starting the server:
```
export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.production
python manage.py runserver
```

This should launch the server on port 8000. Cancel after testing.

#### Updating

Stop server:
```
systemctl stop adhocracy-plus
systemctl stop adhocracy-plus-background-task
```

Switch to user:
```
su aplus
cd ~/adhocracy-plus
```

Enable virtual environment:
```
workon aplus
```

Update the code:

```
git pull
```

Cleanup old static files:
```
rm -rf static/*
```

Install and build again:
```
npm install
npm run build:prod
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.build
python manage.py compilemessages
python manage.py collectstatic
```

Update Database:
```
python manage.py migrate
```

Try starting the server:
```
export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.production
python manage.py runserver
```

This should launch the server on port 8000. Cancel after testing.

Create admin user:
```
python manage.py createsuperuser
```

Restart server (as `root` or using `sudo`)
```
systemctl start adhocracy-plus
systemctl start adhocracy-plus-background-task
```

#### systemd example unit files

Create unit files:
```
$ cat /etc/systemd/system/adhocracy-plus.service:
[Unit]
Description=adhocracy+ server
After=network.target

[Service]
User=aplus
WorkingDirectory=/home/aplus/adhocracy-plus
ExecStart=/home/aplus/.virtualenvs/aplus/bin/gunicorn -e DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.production --workers 4 --threads 2 -b 127.0.0.1:8000 -n adhocracy-plus adhocracy-plus.config.wsgi
Restart=always
RestartSec=3
StandardOutput=append:/var/log/adhocracy-plus/adhocracy-plus.log
StandardError=inherit

[Install]
WantedBy=default.target
```

```
$ cat /etc/systemd/system/adhocracy-plus-background-task.service
[Unit]
Description=adhocracy+ background task
After=network.target

[Service]
User=aplus
WorkingDirectory=/home/aplus/adhocracy-plus
ExecStart=/home/aplus/.virtualenvs/aplus/bin/python manage.py process_tasks --settings adhocracy-plus.config.settings.production --sleep 5
Restart=always
RestartSec=3
StandardOutput=append:/var/log/adhocracy-plus/adhocracy-plus-background-task.log
StandardError=inherit

[Install]
WantedBy=default.target
```

Create log folder:
```
mkdir /var/log/adhocracy-plus
```

Load and start units (as `root` or using `sudo`):
```
systemctl daemon-reload
systemctl start adhocracy-plus
systemctl start adhocracy-plus-background-task
```

Enable autostart on boot:
```
systemctl enable adhocracy-plus
systemctl enable adhocracy-plus-background-task
```

#### nginx example config
```
server {
  listen 80 default_server;
  listen [::]:80 default_server;

  server_name example.com;

  location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8000;
  }

  location /media {
    root /home/aplus/aplus-media;
  }

  client_max_body_size 20m;
}

```

### Contributing
If you found an issue or want to contribute check out [contributing](https://github.com/liqd/adhocracy-plus/blob/master/docs/contributing.md)

## Security
We care about security. So, if you find any issues concerning security, please send us an email at info [at] liqd [dot] net.
