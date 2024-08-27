# Installation Guide - Ariel Research 

We use environment variables to securely store sensitive information such as passwords and keys (e.g., Django's secret key).

## Prerequisites:
Database: We're using Mysql

## Installation

1. Follow the [adhocracy-plus installation guide](https://github.com/ariel-research/adhocracy-plus/README.md).

2. **Create a `.env` File**:  
   Add a `.env` file to the root folder of your project. Below is an example:

    ```env
    DJANGO_SECRET_KEY=dffsfdl^dsadfkmtb34#rf&kdjxnfc
    HOST=100.200.300.400
    PORT=8004
    DOMAIN=aplus.com
    MYSQL_DB=adhocracy
    MYSQL_USERNAME=mysql_username
    MYSQL_PASS=12345678
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_HOST_PASSWORD=dfsadvvgardgtvsfd
    EMAIL_HOST_USER=aplus@aplus.com
    FROM_EMAIL=aplus
    ```

3. **Install `python-dotenv`**:  
   Make sure you have the `python-dotenv` package installed by running:

    ```bash
    pip install python-dotenv
    ```

4. **Load Environment Variables in Your Settings**:  
   In the [settings file](../adhocracy-plus/config/settings/), ensure the environment variables are loaded as follows:

    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```

   You can then access your environment variables like this:

    ```python
    HOST = os.getenv("HOST")
    ```

## Production
1. Run the following commands:

        cd ~/adhocracy-plus
        source venv/bin/activate
        npm run build:prod                 # wait several minutes
        export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.build
        python manage.py compilemessages
        python manage.py collectstatic     # wait several minutes

3. Restart the service:
    ```
    sudo service <service_name> restart
    ```
