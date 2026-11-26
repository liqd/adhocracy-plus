# syntax=docker/dockerfile:1

# The image is built in three stages so that build-only tooling (Node/pnpm,
# uv, compilers, -dev headers, gettext) never ends up in the runtime layer:
#
#   assets       -> node + pnpm, only the compiled JS/CSS is copied over
#   python-deps  -> slim python + uv + compilers/headers, only the venv is copied
#   app          -> slim python + runtime libs + venv + source
#
# The former single-stage build used the full python:3.12-bookworm image and
# kept gdal/geos/proj development headers, git, gettext and the whole dev
# dependency group in the deployed image, which dominated the image size.

# Both Python stages must use the same image: the venv is built in one stage
# and copied into the other, and it references the interpreter and bytecode of
# that exact Python build.
ARG PYTHON_IMAGE=python:3.12-slim-bookworm

# --- 1. Frontend assets ------------------------------------------------------

# pnpm 11 requires Node.js >= 22.13 (uses the built-in node:sqlite module)
FROM node:22-bookworm-slim AS assets

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@11.28.8 --activate

# pnpm needs pnpm-workspace.yaml (allowBuilds for adhocracy4, overrides,
# packageExtensions), the lockfile and .npmrc to install correctly.
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm run build


# --- 2. Python dependencies --------------------------------------------------

FROM ${PYTHON_IMAGE} AS python-deps

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_NO_PROGRESS=1

# Compilers and headers are only needed when a wheel has to be built from
# source (psycopg[c] from the prod extra, any package without a manylinux
# wheel). This stage is discarded, so they never inflate the runtime image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
# The prod extra (psycopg[c], hiredis) instead of the dev group: the image
# only needs to run the app, not the test/lint tooling. gunicorn from that
# extra is only used by the non-Docker deployment (docs/installation_prod.md);
# the container runs granian.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --extra prod --no-install-package gunicorn


# --- 3. Runtime --------------------------------------------------------------

FROM ${PYTHON_IMAGE} AS app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.docker \
    PATH="/app/.venv/bin:$PATH"

# Runtime libraries only:
#   gdal-bin            GeoDjango, ogr2ogr (import_geodata), pulls libgdal32/
#                       libgeos/libproj/proj-data
#   libgeos-c1v5        explicit GEOS runtime for django.contrib.gis
#   libmagic1           python-magic
#   libpq5, libstdc++6  psycopg[c] / bundled native extensions
#   postgresql-client   pg_isready in the entrypoint
# The -dev variants from the old single-stage build are gone.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gdal-bin \
        libgeos-c1v5 \
        libmagic1 \
        libpq5 \
        libstdc++6 \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-deps /app/.venv /app/.venv

WORKDIR /app

COPY . .
COPY --from=assets /app/adhocracy-plus/static /app/adhocracy-plus/static

# gettext is only needed for compilemessages. Installing, compiling and
# purging it in a single RUN keeps it out of the resulting layer.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext \
    && python manage.py compilemessages -v0 \
    && python manage.py collectstatic --noinput \
    && apt-get purge -y --auto-remove gettext \
    && rm -rf /var/lib/apt/lists/*

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8004

ENTRYPOINT ["/entrypoint.sh"]
CMD ["granian", "--interface", "wsgi", "--host", "0.0.0.0", "--port", "8004", "--log-level", "warning", "adhocracy-plus.config.wsgi:application"]
