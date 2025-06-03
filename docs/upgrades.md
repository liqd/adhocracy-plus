# Upgrades for our software -- Django and Wagtail.

Before scheduling upgrades, we need to check version support across Django and Wagtail. For example we may need to upgrade up to a certain version of Django in order to support latest Wagtail, which it supports the latest Django release. Moreover, sometimes we would need to wait for an upgrade due to other dependencies that are not supporting latest releases.

## Django

For Django upgrades, we follow the recommended steps from [Django's official documentation](https://docs.djangoproject.com/en/5.2/howto/upgrade-version/). 
Before starting upgrade, we run the tests with `py.test tests --reuse-db` or `make tests` and we try to fix all deprecation warnings that are related to our code base, and not those related to external installed packages and libraries.
The most thorough step is to look at the release notes of the `final` release from the one after our current Django version, up to and including the version to which we plan to upgrade. E.g if our current version is 4.2.x, we upgrade first to the latest version of this release (that is 4.2.22) and then incrementally to the last release of the next feature release. E.g the next and final feature release of 4.2.x is 5.0.14. We read the release notes of each version we are updating to, and ensure that deprecated and removed coding blocks and features are updated in our code accordingly. 

For each version upgrade we run the tests to check if they pass. 
We then apply the migrations that will affect the Database schema by running the migrate command with `python manage.py migrate`.
If in the process of upgrading we have changed our models, e.g by how the index is declared, or the field, or any change, we need to run `python manage.py makemigrations` and if new migrations files are generated we need to run the migrate command as above. 
We commit each version upgrade separately with a message that includes `django upgrade` + version. This way and in case something went wrong on the live servers, we can revoke back to a previous version more easily.


- All release notes are found [here](https://docs.djangoproject.com/en/5.2/releases/).
- Helpfull tool for upgrading
- Example of a previous [Django upgrade](https://github.com/liqd/adhocracy4/pull/1504/commits). In this PR we see the different commits for each upgrade, and also for each package that needs upgrade before we jump to a higher version that requires said package.

## Wagtail

The process is similar to Django, that we upgrade one feature release at a time, even if our current wagtail version is several versions behind the current one. For example, instead of going from 6.0 directly to 6.3, upgrade to 6.1 and 6.2 first rather than skipping directly to the newest release. For each upgrade, we read though the release notes for feature removals/deprecations, and migrations we need to run similar to the Django upgrade process.

- Official Wagtail upgrade release notes and howto, see [here](https://docs.wagtail.org/en/stable/releases/upgrading.html).
- Example of a previous [Wagtail upgrade](https://github.com/liqd/adhocracy-plus/pull/2868/commits).
