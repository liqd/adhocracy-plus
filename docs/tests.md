# Tests

## Backend Tests

We use pytest in combination with pytest-django and factoryboy to write backend
tests.

### Notes

#### Testing Emails

Emails are not guaranteed to be sent in a deterministic order, so checking
against an index will result in flaky tests. If you want to assert
that a mail was sent use one of the helper functions in `tests/helpers.py`.
