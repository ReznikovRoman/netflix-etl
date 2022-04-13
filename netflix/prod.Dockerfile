FROM python:3.10

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
        gettext \
        postgresql-client-common \
        postgresql-client \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create folder for gunicorn logs
RUN mkdir -p /var/log/gunicorn

# Copy requirements files
COPY requirements/requirements.txt requirements.txt
COPY requirements/requirements.dev.txt requirements.dev.txt
COPY ./requirements/requirements.lint.txt ./requirements.lint.txt

# Install project dependencies
RUN pip install --upgrade pip-tools
RUN pip-sync requirements.txt requirements.*.txt

# Copy configuration files
COPY ./conf /app/conf

# Copy project files
COPY . .

# Expose 8000 port
EXPOSE 8000

# Run docker entrypoint
RUN chmod +x /app/conf/docker/entrypoint.sh
ENTRYPOINT ["/app/conf/docker/entrypoint.sh"]

# Spin up server
CMD ["django-cadmin", "runserver_plus", "--print-sql", "0.0.0.0:8000"]
