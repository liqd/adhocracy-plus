# PostgreSQL
Add the `DATABASE` settings in the `adhocracy_plus/config/settings/local.py`. You can copy the `DATABASE` configuration block from `adhocracy-plus/config/settings/base.py` and then update the `user`, `name`, and other relevant settings. Also, consider specifying a password, as leaving it out could cause connection issues with recent postgresql versions.
To avoid potential conflicts, we recommend choosing a different name for your database instead of the default `django`, as this could interfere with other projects’ databases that use also the default name later on. However in the make command we use `django` for the database_name.

See howto install [PostgreSQL for your Operating System](https://www.postgresql.org/download)

Install the [Postgis Extension](https://www.postgis.net/documentation/getting_started#installing-postgis)

Assuming you have postgresql installed and running; switch to postgres user from the command line with `sudo su postgres`.

In the commands below, be sure to replace `database_name` and `user_name` with your preferred names set in your local.py.

Enter the postgresql shell with the command `psql`.
```
$ psql 
psql (15.12 (Debian 15.12-0+deb12u2))
Type "help" for help.

postgres=# CREATE USER user_name;

postgres=# GRANT ALL ON SCHEMA public TO user_name;
GRANT

postgres=# CREATE DATABASE database_name;

postgres=# ALTER DATABASE database_name OWNER TO user_name;
ALTER DATABASE

postgres=# GRANT ALL PRIVILEGES ON DATABASE database_name to user_name;
GRANT

postgres=# ALTER USER user_name WITH PASSWORD 'your_new_password';

postgres=# \c database_name;
You are now connected to database "database_name" as user "postgres".
database_name=# CREATE EXTENSION postgis WITH SCHEMA public;
```
