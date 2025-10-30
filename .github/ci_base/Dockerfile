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
        nodejs \
        npm \
        git \
        python3 \
        python3-pip \
        python3-venv \
        libmagic1 \
        libmagic-dev && \
    rm -rf /var/lib/apt/lists/*

# Install uv system-wide
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv

# Configure PostgreSQL
RUN service postgresql start && \
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';" && \
    sudo -u postgres createdb django && \
    sudo -u postgres createdb django_test && \
    sudo -u postgres psql -d django -c "CREATE EXTENSION IF NOT EXISTS postgis;" && \
    sudo -u postgres psql -d django_test -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Additional tools that are always needed
# RUN npm install -g some-global-node-tool # Example for Node-Tools
# RUN pip install poetry # Example for Python-Tools

# Set the working directory
WORKDIR /app
