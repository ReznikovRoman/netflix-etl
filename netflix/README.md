# Netflix*

## Настройка и запуск

Docker конфигурации содержат контейнеры:
1. db (postgres)
2. server (django, gunicorn)

Для успешного запуска необходимо указать переменные окружения в файле `.env` в корне проекта.

**Формат `.env` файла:**

```
ENV=.env

# Django
DJANGO_SETTINGS_MODULE=netflix.settings
DJANGO_CONFIGURATION=Local
DJANGO_ADMIN=django-cadmin
DJANGO_SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1

# Project
PROJECT_BASE_URL=http://localhost:8000

# Media
MEDIA_URL=/media/
STATIC_URL=/staticfiles/

# Postgres
DB_HOST=db
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DECODE_RESPONSES=1

# Elasticsearch
ES_HOST=elasticsearch
ES_PORT=9200

# ETL
DB_POSTGRES_BATCH_SIZE=500
ES_TIMEOUT=3
```

В локальной конфигурации docker-compose нет контейнера `nginx`,
а сервер запускается командой django-cadmin runserver_plus.
Для локальной конфигурации также необходимо создать файл конфигурации Django `tb_content/settings/local.py`:

```python
import mimetypes
import socket

from .base import Base
from .values import from_environ


class Local(Base):
    DEBUG = True
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = [
        'http://127.0.0.1:8000',
        'http://localhost:8000',
    ]

    STATIC_URL = "staticfiles/"

    LOG_SQL = from_environ(name='PROJECT_LOG_SQL', type=bool, default=False)

    # debug toolbar
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda show_toolbar: True,
    }
    mimetypes.add_type('application/javascript', '.js', True)

    DEV_INSTALLED_APPS = [
        "debug_toolbar",
    ]
    DEV_MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

    Base.INSTALLED_APPS.extend(DEV_INSTALLED_APPS)
    Base.MIDDLEWARE.extend(DEV_MIDDLEWARE)

```

**Запуск производится в два этапа:**

```
docker-compose build
docker-compose up
```

**Для успешного прохождения тестов в Postman нужно заполнить БД тестовыми данными**
```shell
docker-compose run --rm server bash -c "cd /app/scripts/load_db && python load_data.py"
```

При старте gunicorn контейнера выполняется применение миграций и сбор статики.

Перезапуск контейнеров вручную происходит в один этап:

```
docker-compose restart
```

## Разработка

В проекте используется [`django-configurations`](https://django-configurations.readthedocs.io/en/latest/), поэтому для выполнения management команд Django вместо `./manage.py` / `python -m django` / `django-admin` следует использовать `django-cadmin`.

**Пример: Создание суперпользователя**
```shell
django-cadmin createsuperuser
```

Синхронизировать окружение с `requirements.txt` / `requirements.dev.txt` (установит отсутствующие пакеты, удалит лишние, обновит несоответствущие версии):

```shell
make sync-requirements
```

Перегенерировать `requirements.txt` / `requirements.dev.txt` (требуется после изменений в `requirements.in` / `requirements.dev.in`):

```shell
make compile-requirements
```

Если в окружении требуется установить какие-либо пакеты, которые нужно только локально разработчику, то следует создать файл `requirements.local.in` и указывать зависимости в нём. Обязательно следует указывать constraints files (`-c ...`). Например, чтобы запускать `shell_plus` c `ptipython` (`django-cadmin shell_plus --ptipython`), нужно поставить пакеты `ipython` и `ptpython`, в таком случае файл `requirements.local.in` будет выглядеть примерно так (первые строки одинаковы для всех, остальное — зависимости для примера):

```
-c requirements.txt
-c requirements.dev.txt

ipython >=7, <8
ptpython >=3, <4
```

Перед пушем коммита следует убедиться, что код соответствует принятым стандартам и соглашениям:

```shell
make lint
```

## Документация API

Документация в формате OpenAPI 3 доступна по адресу:

* `${PROJECT_BASE_URL}/api/v1/schema` (YAML или JSON, выбор через content negotiation заголовком `Accept`)
* `${PROJECT_BASE_URL}/api/v1/schema/redoc` (ReDoc)
* `${PROJECT_BASE_URL}/api/v1/schema/swagger` (Swagger UI)

___
##### *_kinopoisk_
