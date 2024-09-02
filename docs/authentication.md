# Authentication

We use [Django Allauth](https://docs.allauth.org/) for handling user registration, email and social logins via the browser.

For API authentication we setup Django Rest Framework with Simple JWT for authentication via JWT tokens. Existing users can obtain JWT tokens through the TokenObtainPairView. We haven't enabled JWT based registration yet, as this is an implementation for an external partner, and not as part of the software architecture exposing API registration with JWT.

Login: Users can obtain JWT tokens via the `/api/token/` endpoint.
For testing via the terminal try:
```
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin","password": "password"}' http://adhocracy.plus/api/token/

```
For testing in dev and stage servers replace the domain name with `http://aplus-dev.liqd.net/api/token/` and `http://aplus-stage.liqd.net/api/token/` respectively.
Make sure to use your corresponding user credentials (username, password).

The response of the above command, will include an access and a refresh token.

For accessing the projects list endpoint `/api/app-projects/`, user need to supply the obtained JWT token.
E.g testing via the terminal with:
```
curl -H "Authorization: Bearer <access token from the response>" https://adhocracy.plus/api/app-projects/ 
```

For accessing a project details, we can lookup the `slug` key from the projects list, and call the endpoint `/api/app-projects/app-testing/`, where the slug is `app-testing`.
E.g for testing in the terminal, we can run:
```
curl -H "Authorization: Bearer <access token from the response>" https://aplus-dev.liqd.net/api/app-projects/app-testing/
```

The expiration time for JWT access token is 5hrs, after which the user can refresh it by calling the `api/token/refresh/` with the `refresh` token obtained during login.
Refresh token expires after 1 day. They expiration times are set in the settings file `adhocracy-plus/config/settings/base.py` as `SIMPLE_JWT`.

For more info about how to obtain and refresh a token, visit the [django restframework simple jwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html#usage) docs.

