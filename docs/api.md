# API

## users and permissions
We enabled token authentification in a+. So to use the APIs,
the user token has to be given instead of name and password.

To generate or get the token in the terminal:
`curl -X POST http://localhost:8004/api/login/ -H 'Accept: application/json;' -d 'username=$username&password=$password'`
`{"token":"$some_quite_long_token"}`

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
