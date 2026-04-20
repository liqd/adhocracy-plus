# Use the official Python image as the base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DATABASE sqlite

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev sqlite3 nodejs npm redis-server libmagic1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /adhocracy-plus

# Copy the requirements file
COPY requirements.txt .
COPY /requirements /adhocracy-plus/requirements

# Create a virtual environment and install Python dependencies
RUN python -m venv /adhocracy-plus/venv && \
    /bin/bash -c "source /adhocracy-plus/venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Copy the rest of the application code
COPY . .

# Create a non-root user and set permissions
RUN useradd -ms /bin/bash appuser && \
    chown -R appuser:appuser /adhocracy-plus

RUN chmod +x /adhocracy-plus/entrypoint.sh

# Switch to the non-root user
USER appuser

# Install Node.js dependencies
RUN npm install

# Set up the database
RUN /bin/bash -c "source /adhocracy-plus/venv/bin/activate && make install && make fixtures"

RUN ls /adhocracy-plus
# Expose the application port
EXPOSE 8004

# Set the entry point for the container
ENTRYPOINT ["/adhocracy-plus/entrypoint.sh"]
