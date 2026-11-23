# ci-base/Dockerfile
FROM ubuntu:24.04

# Install the OS dependencies
RUN apt update && \
    apt install -y \
        gdal-bin \
        libsqlite3-mod-spatialite \
        postgresql-client \
        postgresql \
        postgresql-contrib \
        postgresql-16-postgis-3 \
        curl \
        unzip \
        sudo \
        jq \
        git \
        python3 \
        python3-venv \
        libmagic1 \
        libmagic-dev && \
    rm -rf /var/lib/apt/lists/*

# Keep uv in the image: main and open PRs still use it. Remove once the
# setup-uv workflow is on main.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv

# Configure PostgreSQL
RUN service postgresql start && \
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';" && \
    sudo -u postgres createdb django && \
    sudo -u postgres createdb django_test && \
    sudo -u postgres psql -d django -c "CREATE EXTENSION IF NOT EXISTS postgis;" && \
    sudo -u postgres psql -d django_test -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Set the working directory
WORKDIR /app