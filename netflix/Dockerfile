FROM python:3.10

ARG PIP_EXTRA_INDEX_URL

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

WORKDIR /app

# Copy requirements files
COPY requirements/requirements.txt requirements.txt
COPY requirements/requirements.dev.txt requirements.dev.txt
COPY ./requirements/requirements.lint.txt ./requirements.lint.txt

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

# Install project dependencies
RUN pip install --upgrade pip-tools
RUN pip-sync requirements.txt requirements.*.txt

CMD ["bash"]
