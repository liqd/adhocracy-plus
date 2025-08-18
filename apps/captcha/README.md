# Prosopo Captcha Integration

This integration adds the [Prosopo Captcha System](https://docs.prosopo.io/en/basics/) to adhocracy-plus.

## Installation

### 1. Create Prosopo Account

1. Visit [https://docs.prosopo.io/en/basics/](https://docs.prosopo.io/en/basics/)
2. Create an account and navigate to "Site Management"
3. Create a new site and copy the Site Key and Secret Key


### 2. Configure Settings

Add the following configuration to your local settings file (`local.py`):

```python
# Prosopo Captcha Configuration
CAPTCHA = True
PROSOPO_SITE_KEY = "your_site_key_here"
PROSOPO_SECRET_KEY = "your_secret_key_here"
```


## Additional Information

- [Prosopo Documentation](https://docs.prosopo.io/en/basics/)
- [Prosopo GitHub](https://github.com/prosopo)
- [Prosopo Discord](https://discord.gg/prosopo)
