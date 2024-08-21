# Running Tests
> **Note: Ensure that your virtual environment is activated before running commands.**
## Django Tests

1. **Import Tests**:  
   Ensure that the tests are imported into the `__init__.py` file located in the `apps/<app_name>/tests` folder. For example:

    ```python
    from .test_fairvote_sn import *
    ```

2. **Run Tests**:  
   To run the tests, call the appropriate test class or specific test method.  
   - To run a single test:

    ```bash
    python manage.py test apps.fairvote.tests.fairVoteSNTestCase.test_sn_users
    ```

   - To run all tests in a file:

    ```bash
    python manage.py test apps.fairvote.tests.fairVoteSNTestCase
    ```

## Running Django Code (Saving Data in the Database)

1. **Set Up Django Environment**:  
   At the top of your file, import `os` and `django`, and load the Django settings:

    ```python
    import os
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adhocracy-plus.config.settings")
    django.setup()
    ```

2. **Import Models**:  
   After setting up the environment, you can import your Django models and apps. For example:

    ```python
    from allauth.account.models import EmailAddress
    from adhocracy4.ratings.models import Rating
    from apps.fairvote.models import Choin
    ```

3. **Locate the File**:  
   Place the script in the root directory of your project.

4. **Run the Script**:  
   Execute the file using the following command:

    ```bash
    python <file_name>.py
    ```