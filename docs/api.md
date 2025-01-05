# API

## User Dashboard API
### serializers

::: apps.userdashboard.serializers
### views

::: apps.userdashboard.views


## users and permissions
We enabled token authentification in a+. So to use the APIs,
the user token has to be given instead of name and password.

To generate or get the token in the terminal:
`curl -X POST http://localhost:8004/api/login/ -H 'Accept: application/json;' -d 'username=$username&password=$password'`
`{"token":"$some_quite_long_token"}`

## Projects API

### serializers

::: apps.projects.serializers
### views

::: apps.projects.api

We can access a list of the projects with an API endpoint.
Projects that are returned are public or semi-public, are currently running, or scheduled for future, and are not draft nor archived, and have geolocation enabled by their organisation.
The query filtering of the projects happens inside the `projects/api.py` and are customised according to our external partner WeChange. We may consider to implement a seperate django filter later.

E.g testing via the terminal with:
```
curl -X GET http://localhost:8004/api/app-projects/ -H 'Authorization: Token $some_quite_long_token'
```

## Idea API
To create, update and delete ideas from the app, we added an API for ideas.

To use it to add an idea:
`curl -X POST http://localhost:8004/api/modules/$moduleId/ideas/ -H 'Accept: application/json;' -H 'Authorization: Token $some_quite_long_token' -d 'name=my name&description=my description'`

If the idea, requires a category, use it with the pk of the category:
`curl -X POST http://localhost:8004/api/modules/$moduleId/ideas/ -H 'Accept: application/json;' -H 'Authorization: Token $some_quite_long_token' -d 'name=my name&description=my description&category=1'`

To post many ideas very quickly, use a shell-script like this one:
```
for i in {1..10}
do
curl -X POST http://localhost:8004/api/modules/$moduleId/ideas/ -H 'Accept: application/json;' -H 'Authorization: Token $some_quite_long_token' -d 'name=my name&description=my description&category=1'
done
```
