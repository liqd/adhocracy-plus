#!/usr/bin/env bash
set -euo pipefail

postgres_host="${POSTGRES_HOST:-db}"
postgres_port="${POSTGRES_PORT:-5432}"
postgres_user="${POSTGRES_USER:-django}"
postgres_db="${POSTGRES_DB:-django}"

echo "Waiting for PostgreSQL at ${postgres_host}:${postgres_port}..."
until pg_isready -h "${postgres_host}" -p "${postgres_port}" -U "${postgres_user}" -d "${postgres_db}" >/dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready."

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  python manage.py migrate --noinput

  fixtures_marker="/app/media/.docker-fixtures-loaded"
  if [ "${LOAD_FIXTURES:-1}" = "1" ] && [ ! -f "${fixtures_marker}" ]; then
    echo "Loading development fixtures (site, organisation)..."
    python manage.py loaddata adhocracy-plus/fixtures/site-dev.json

    if [ "${LOAD_USER_FIXTURES:-0}" = "1" ]; then
      python manage.py loaddata adhocracy-plus/fixtures/users-dev.json
      python manage.py loaddata adhocracy-plus/fixtures/orga-dev.json
    else
      python manage.py loaddata adhocracy-plus/fixtures/orga-dev-docker.json
    fi

    mkdir -p "$(dirname "${fixtures_marker}")"
    touch "${fixtures_marker}"
  elif [ "${LOAD_USER_FIXTURES:-0}" = "1" ] && [ ! -f "/app/media/.docker-user-fixtures-loaded" ]; then
    echo "Loading user fixtures..."
    python manage.py loaddata adhocracy-plus/fixtures/users-dev.json
    touch "/app/media/.docker-user-fixtures-loaded"
  fi
else
  echo "Waiting for database migrations (web service)..."
  until python manage.py migrate --check >/dev/null 2>&1; do
    sleep 2
  done
  echo "Database schema is ready."
fi

exec "$@"
