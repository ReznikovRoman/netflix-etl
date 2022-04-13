FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        gcc \
        musl-dev \
        libc-dev \
        libcurl4-gnutls-dev \
        librtmp-dev \
        postgresql-client-common \
        postgresql-client \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements/requirements.txt requirements.txt

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy configuration files
COPY ./conf /app/conf

# Copy project files
COPY . .

# Spin up etl service
CMD ["python", "elastic.py"]
