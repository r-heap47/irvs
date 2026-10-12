# ИРВС, ДЗ №1: приложение + PostgreSQL в Docker Compose

Небольшой REST-сервис заметок на **Python 3.12 + FastAPI**, который хранит данные в **PostgreSQL 16**.
Приложение собирается из `Dockerfile` и запускается вместе с БД через `compose.yaml`.

## Структура

```
app/main.py      — FastAPI-приложение (CRUD заметок + /health)
db/init.sql      — схема БД, выполняется postgres при первом запуске
Dockerfile       — образ приложения (python:3.12-slim, непривилегированный пользователь)
compose.yaml     — сервисы app и db, том pgdata, healthcheck
.env.example     — пример переменных окружения
```

## Запуск

```bash
cp .env.example .env    # при желании поменяйте пароль и порт
docker compose up --build
```

Приложение будет доступно на `http://localhost:8000` (порт задаётся `APP_PORT` в `.env`),
интерактивная документация — `http://localhost:8000/docs`.
Порт PostgreSQL наружу не публикуется: приложение ходит в БД по имени сервиса `db` внутри сети compose.
`app` стартует только после того, как `db` пройдёт healthcheck (`pg_isready`).

## Примеры запросов

```bash
# проверка приложения и соединения с БД
curl localhost:8000/health
# {"status":"ok","db":"ok"}

# создать заметку
curl -X POST localhost:8000/notes \
     -H 'Content-Type: application/json' \
     -d '{"title": "Первая заметка", "body": "Привет из Docker"}'

# список заметок
curl localhost:8000/notes

# заметка по id
curl localhost:8000/notes/1

# удалить заметку
curl -X DELETE localhost:8000/notes/1
```

## Остановка

```bash
docker compose down       # остановить контейнеры, данные в томе pgdata сохранятся
docker compose down -v    # остановить и удалить том с данными
```

Схема из `db/init.sql` применяется только при инициализации пустого тома,
поэтому после изменения схемы нужно выполнить `docker compose down -v`.
