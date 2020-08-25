# Installation guide for production systems

This guide will focus on Debian/Ubuntu-like systems - however, it works very similar on e.g. Fedora and friends.

## Required packages:
 * python3
 * python3-pip
 * virtualenvwrapper
 * gettext
 * git
 * curl
 * nodejs ([in an up-to-date version](https://github.com/nodesource/distributions/blob/master/README.md))
 * nginx / apache webserver
 * optionally: a database like postgresql / mariadb

## Step-by-step setup

### Create user
Create and switch to user (as `root` or using `sudo`)

```
adduser aplus
su aplus
cd
```

### Get the code
```
git clone https://gitlab.cs.uni-duesseldorf.de/diid/diid_adplus.git
cd diid_adplus
git checkout release
```

### Create and launch virtual environment
```
mkvirtualenv --python=/usr/bin/python3 aplus
```

Note: you won't need the `--python` part when using a recent distribution.

### Install dependencies and build static optimized JS code
```
npm install
npm run build:prod
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.build
python manage.py compilemessages
python manage.py collectstatic
```

### Static configuration (`local.py`)

Create a config file at `~/adhocracy-plus/adhocracy-plus/config/settings/local.py`

See the [django-documentation](https://docs.djangoproject.com/en/2.2/ref/settings/) for a comprehensive list of settings and `config/settings/base.py` for pre-configured ones. The settings you will most likely want to set are:

```
# replace 'example.com' with your desired domain
ALLOWED_HOSTS = [u'your.domain', u'localhost']

# database config - we recommend postgresql for production purposes
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'aplus-test-database',
  }
}

# forward outgoing emails to a local email proxy
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='127.0.0.1'

# folder for user-uploads, directly served from the webserver (see nginx example below). Must be created manually.
MEDIA_ROOT='/home/aplus/aplus-media'

# replace the value below with some random value
SECRET_KEY = u'SOMESECRETKEY'

# some basic security settings for serving the website over https - see django docu
CSRF_COOKIE_SECURE=True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True

FILE_UPLOAD_PERMISSIONS = 0o644
```

### Populate database

This will create all required tables via so called **migrations**

```
python manage.py migrate
```

### Test run

Try starting the server:

```
export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.production
python manage.py runserver
```

From another terminal on the same server:

```
curl localhost:8000
```

You should now get valid HTML output.

Cancel the server after testing via `ctrl`+`c`

## Run the server as system daemon

In order to start up the software as a regular system daemon, similar to a database or webserver, we need to create unit files.

`/etc/systemd/system/adhocracy-plus.service`:

```
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

`/etc/systemd/system/adhocracy-plus-background-task.service`:

```
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

This will log all output to files in `/var/log/adhocracy-plus/`. You will also need to create that folder before starting the service (as `root` or using `sudo`):

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

## Setting up a proxy webserver

Finally, we need to set up a proxy webserver which handles the communication with the outside world. The following example is a simple config for `nginx`:

```
server {
  listen 80;
  listen [::]:80;

  # for using https - see nginx docu
  #listen 443 ssl http2;
  #listen [::]:443 ssl http2;

  server_name your.domain;

  # forward traffic to adhocracy-plus
  location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8000;
  }

  # serve media files directly, without going through adhocracy-plus.
  # See MEDIA_ROOT in local.py
  location /media {
    alias /home/aplus/aplus-media;
  }

  # max upload size for images and documents
  client_max_body_size 20m;
}

```

The website should now be reachable

## Admin user and first organization

You can now continue setting up the website in the `django-admin` configuration page. Please also see the [manual](https://manual.adhocracy.plus/) for a more comprehensive documentation.

### Create initial admin user

```
su aplus
cd ~/adhocracy-plus
workon aplus
python manage.py createsuperuser
```

### Django-admin

Visit `http[s]://your.domain/django-admin` and log in with the user you just created.

### Domain settings

In the `sites` (german: `Websites`) section, change the domain name of the existing site to `your.domain`

### First organisation

In the `Organisations` section, add a new organization. For the moment, all you need is setting the name and adding you user to the `Initiators`.

You can now visit `http[s]://your.domain/` and select the organization from the user dropdown menu - it will bring you to the `dashboard`. See the [manual](https://manual.adhocracy.plus/).

### Landing page

The landing page is managed via [wagtail](https://wagtail.io/). You can find the settings at `http[s]://your.domain/admin`.

## Updating

### Stop server

```
systemctl stop adhocracy-plus
systemctl stop adhocracy-plus-background-task
```

### Switch to user

```
su aplus
cd ~/adhocracy-plus
```

###  Enable virtual environment

```
workon aplus
```

### Update the code

```
git pull
```

### Cleanup old static files

```
rm -rf static/*
```

### Update dependencies and rebuild static optimized JS code

```
npm install
npm run build:prod
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.build
python manage.py compilemessages
python manage.py collectstatic
```

### Update Database

```
python manage.py migrate
```

### Try starting the server

```
export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.production
python manage.py runserver
```

### Restart server (as `root` or using `sudo`)

```
systemctl start adhocracy-plus
systemctl start adhocracy-plus-background-task
```

## SAML2 / Shibolleth configuration for DIID

SAML2 currently does not integrate very well into the `django-allauth` system, thus some extra configuration is required.

### Required packages

  * xmlsec1

### Configuration

Add the following to your `local.py` and adapt as necassary:

```
import os
from os import path
import saml2
import saml2.saml

BASEDIR = path.dirname(path.abspath(__file__))

SAML_CONFIG = {
  'xmlsec_binary': '/usr/bin/xmlsec1',
  'entityid': 'https://your.domain/saml2/metadata/',
  'allow_unknown_attributes': True,
  'attribute_map_dir': path.join(BASEDIR, 'attribute-maps'),
  'service': {
    'sp': {
      'name': 'Federated Django sample SP',
      'name_id_format': saml2.saml.NAMEID_FORMAT_PERSISTENT,
      'allow_unsolicited': True,
      'endpoints': {
        'single_logout_service': [
          ('https://your.domain/saml2/ls/post', saml2.BINDING_HTTP_POST),
          ('https://your.domain/saml2/ls/', saml2.BINDING_HTTP_REDIRECT),
        ],
        'assertion_consumer_service': [
          ('https://your.domain/saml2/acs/', saml2.BINDING_HTTP_POST),
        ],
      },
      'required_attributes': ['mail'],
    },
  },
  'metadata': {
    # Only use the HHU IDP
    'remote': [{"url": "https://idp.uni-duesseldorf.de/idp/shibboleth"},],
    # Allow all members of in the DNF - comment out the remote above if used
    #'remote': [{"url": "https://www.aai.dfn.de/fileadmin/metadata/dfn-aai-test-metadata.xml"},],
  },
  'key_file': path.join(BASEDIR, 'saml', 'private.key'),  # private part
  'cert_file': path.join(BASEDIR, 'saml', 'cert.pem'),  # public part
  'encryption_keypairs': [{
    'key_file': path.join(BASEDIR, 'saml', 'private.key'),  # private part
    'cert_file': path.join(BASEDIR, 'saml', 'cert.pem'),  # public part
  }],
  'valid_for': 17520,
}
SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'
SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_REDIRECT
SAML_ATTRIBUTE_MAPPING = {
    'mail': ['email', 'set_username_from_email'],
}
```

### Key and cert

In the `settings` folder, where your `local.py` resides, create a new key and cert:

```
mkdir saml
cd saml
openssl req -x509 -nodes -newkey rsa:4096 -keyout private.key -out cert.pem -days 365
```

### Registering

Restart the server and you can find you metadate at `https://your.domain/saml2/metadata/`. These are needed in order to register your instance with the IDP. Once the registration is done, you should be able to login using Shibolleth.
