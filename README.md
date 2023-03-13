# Netflix ETL
_Netflix_ ETL pipelines for syncing data between Postgres and Elasticsearch.

## Stack
[Postgres](https://www.postgresql.org/), [Elasticsearch](https://www.elastic.co/what-is/elasticsearch),
[Redis](https://redis.io/)

## Services
- Netflix Admin:
  - Online-cinema management panel. Admins can manage films, genres, actors/directors/writers/...
  - https://github.com/ReznikovRoman/netflix-admin
- Netflix ETL:
  - ETL pipeline for synchronizing data between "Netflix Admin" database and Elasticsearch
  - https://github.com/ReznikovRoman/netflix-etl
- Netflix Movies API:
  - Movies API
  - https://github.com/ReznikovRoman/netflix-movies-api
    - Python client: https://github.com/ReznikovRoman/netflix-movies-client
- Netflix Auth API:
  - Authorization service - users and roles management
  - https://github.com/ReznikovRoman/netflix-auth-api
- Netflix UGC:
  - Service for working with user generated content (comments, likes, film reviews, etc.)
  - https://github.com/ReznikovRoman/netflix-ugc
- Netflix Notifications:
  - Notifications service (email, mobile, push)
  - https://github.com/ReznikovRoman/netflix-notifications
- Netflix Voice Assistant:
  - Online-cinema voice assistant
  - https://github.com/ReznikovRoman/netflix-voice-assistant

## Configuration
Docker containers:
1. redis
2. elasticsearch
3. kibana
4. etl
5. db_admin
6. server_admin

docker-compose files:
 1. `docker-compose.yml` - for local development.

To run docker containers, you need to create a `.env` file in the root directory.

**`.env` example:**
```dotenv
ENV=.env

# Netflix Admin
# Django
DJANGO_SETTINGS_MODULE=netflix.settings
DJANGO_CONFIGURATION=External
DJANGO_ADMIN=django-cadmin
DJANGO_SECRET_KEY=7)%31(changeme12@g87_h8vthi4dj=1pjp^ysv*tnm_fx$$fw6
ALLOWED_HOSTS=localhost,127.0.0.1

# Project
NA_PROJECT_BASE_URL=http://localhost:8000

# Media
NA_MEDIA_URL=/media/
NA_STATIC_URL=/staticfiles/

# Postgres
NA_DB_HOST=db_admin
NA_DB_PORT=5432
NA_DB_NAME=netflix
NA_DB_USER=test
NA_DB_PASSWORD=yandex

# Scripts
NA_DB_POSTGRES_BATCH_SIZE=500

# Netflix ETL
# Redis
NE_REDIS_HOST=redis
NE_REDIS_PORT=6379
NE_REDIS_DECODE_RESPONSES=1

# Elasticsearch
NE_ES_HOST=elasticsearch
NE_ES_PORT=9200
NE_ES_RETRY_ON_TIMEOUT=1
```

### Start project:

Locally:
```shell
docker compose build
docker compose up
```

**To fill DB with test data**
```shell
docker compose run --rm server bash -c "cd /app/scripts/load_db && python load_data.py"
```

## Development
Sync environment with `requirements.txt` / `requirements.dev.txt` (will install/update missing packages, remove redundant ones):
```shell
make sync-requirements
```

Compile requirements.\*.txt files (have to re-compile after changes in requirements.\*.in):
```shell
make compile-requirements
```

Use `requirements.local.in` for local dependencies; always specify _constraints files_ (-c ...)

Example:
```shell
# requirements.local.txt

-c requirements.txt

ipython
```

### Code style:
Before pushing a commit run all linters:

```shell
make lint
```
