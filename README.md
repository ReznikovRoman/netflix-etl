# Netflix ETL

ETL пайплайны для онлайн-кинотеатра _Netflix_.

## Сервисы
- Netflix Admin:
  - Панель администратора для управления онлайн-кинотеатром (редактирование фильмов, жанров, актеров)
  - https://github.com/ReznikovRoman/netflix-admin
- Netflix ETL:
  - ETL пайплайн для синхронизации данных между БД сервиса Netflix Admin и Elasticsearch
  - https://github.com/ReznikovRoman/netflix-etl
- Netflix Movies API:
  - АПИ фильмов
  - https://github.com/ReznikovRoman/netflix-movies-api
- Netflix Auth API:
  - Сервис авторизации - управление пользователями и ролями
  - https://github.com/ReznikovRoman/netflix-auth-api
- Netflix UGC:
  - Сервис для работы с пользовательским контентом
  - https://github.com/ReznikovRoman/netflix-ugc

## Настройка и запуск

Docker конфигурации содержат контейнеры:
1. redis
2. elasticsearch
3. kibana
4. etl
5. db_admin (postgres)
6. server_admin (django)

Для успешного запуска необходимо указать переменные окружения в файле `.env` в корне проекта.

**Формат `.env` файла:**
```dotenv
ENV=.env

# Netflix Admin
# Django
DJANGO_SETTINGS_MODULE=netflix.settings
DJANGO_CONFIGURATION=External
DJANGO_ADMIN=django-cadmin
DJANGO_SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1

# Project
NA_PROJECT_BASE_URL=http://localhost:8000

# Media
NA_MEDIA_URL=/media/
NA_STATIC_URL=/staticfiles/

# Postgres
NA_DB_HOST=db_admin
NA_DB_PORT=5432
NA_DB_NAME=
NA_DB_USER=
NA_DB_PASSWORD=

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
```

**Запуск производится в два этапа:**

```shell
docker-compose build
docker-compose up
```

**Для заполнения БД тестовыми данными**
```shell
docker-compose run --rm server bash -c "cd /app/scripts/load_db && python load_data.py"
```

Перезапуск контейнеров вручную происходит в один этап:

```
docker-compose restart
```

## Разработка
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
