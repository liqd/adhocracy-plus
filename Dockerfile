# syntax=docker/dockerfile:1

# pnpm 11 requires Node.js >= 22.13 (uses the built-in node:sqlite module)
FROM node:22-bookworm-slim AS assets

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@11.8.0 --activate

# pnpm needs pnpm-workspace.yaml (allowBuilds for adhocracy4, overrides,
# packageExtensions), the lockfile and .npmrc to install correctly.
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm run build


FROM python:3.12-bookworm AS app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.docker

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gdal-bin \
        libgdal-dev \
        libgeos-dev \
        libproj-dev \
        libpq-dev \
        gettext \
        postgresql-client \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements requirements
RUN pip install --no-cache-dir -r requirements/dev.txt

COPY . .
COPY --from=assets /app/adhocracy-plus/static /app/adhocracy-plus/static

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8004

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8004"]
