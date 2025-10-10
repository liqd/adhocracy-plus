# ARPAS

## Development

ARPAS uses WebXR which requires an HTTPS connection even in development. To proxy your local development server with HTTPS, you can use [ngrok](https://ngrok.com/).

```bash
ngrok http 8004
```

You may run into an issue with the host not being allowed by Django. To fix this, create the file "adhocracy-plus/config/settings/local.py" with the following content:

```python
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.ngrok-free.app']
```
