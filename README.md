# JWT Auth Redis — Authentication & Authorization System

Полнофункциональная система аутентификации и авторизации на базе **JWT токенов**, **Redis** для управления черным/белым списками токенов, **PostgreSQL** для хранения данных пользователей и контента, с поддержкой **ролевого доступа** к контенту.

## 📋 Содержание

- [Описание](#описание)
- [Архитектура](#архитектура)
- [Требования](#требования)
- [Установка](#установка)
- [Запуск](#запуск)
- [API Endpoints](#api-endpoints)
- [Использование](#использование)
- [Безопасность](#безопасность)
- [Docker](#docker)

---

## 📙 Описание

Проект реализует современную систему управления доступом на основе:

- **JWT (JSON Web Tokens)** — для создания и верификации токенов доступа
- **Redis** — для управления состоянием токенов:
  - ✅ Белый список (whitelist) — активные токены
  - ❌ Черный список (blacklist) — отозванные/заблокированные токены
- **PostgreSQL** — для персистентного хранилища пользователей и контента
- **FastAPI** — современный асинхронный фреймворк
- **SQLAlchemy** — ORM для работы с БД
- **Ролевой контроль доступа (RBAC)** — управление доступом на основе ролей

### Ключевые возможности

✅ Регистрация и аутентификация пользователей  
✅ JWT access + refresh токены  
✅ Безопасный logout с инвалидацией токенов  
✅ Система ролей (role1 и role2)  
✅ Ролевой доступ к контенту  
✅ Redis whitelist/blacklist для проверки состояния токена  
✅ Асинхронная обработка запросов  
✅ Полная контейнеризация (Docker + Docker Compose)

---

## 🏗️ Архитектура

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP Request
       ▼
┌──────────────────────┐
│   FastAPI (main)     │
├──────────────────────┤
│  ├─ /auth            │  Регистрация, Login, Logout, Refresh
│  ├─ /users           │  Получение профиля пользователя
│  └─ /content         │  Доступ к контенту согласно роли
└──────┬────────┬──────┘
       │        │
   ┌───▼─┐  ┌──▼───┐
   │ PG  │  │Redis │
   │ SQL │  │      │
   └─────┘  └──────┘
```

### Компоненты

**FastAPI Routes:**

- `app/api/v1/auth.py` — Endpoints аутентификации
- `app/api/v1/users.py` — Endpoints профиля пользователя
- `app/api/v1/content.py` — Endpoints управления контентом

**Services:**

- `app/services/auth_service.py` — Бизнес-логика (регистрация, login, refresh)

**Security:**

- `app/core/security.py` — Функции для создания/проверки JWT, хеширования пароль

**Database:**

- `app/db/models/` — ORM модели (User, Role, Content)
- `app/db/session.py` — Конфигурация SQLAlchemy
- Alembic миграции в папке `alembic/`

**Redis:**

- `app/core/redis.py` — Работа с Redis (whitelist/blacklist)

**Dependencies:**

- `app/api/deps.py` — Dependency injection (получение текущего пользователя, БД)

---

## ⚙️ Требования

- **Python 3.10+**
- **PostgreSQL 13+**
- **Redis 7+**
- **Docker & Docker Compose** (опционально, для контейнеризации)

### Python пакеты

```
FastAPI==0.135.3
SQLAlchemy==2.x
asyncpg==0.31.0
redis==7.4.0
python-jose==3.5.0
passlib==1.7.4
bcrypt==5.0.0
pydantic-settings==2.13.1
python-dotenv==1.2.2
```

---

## 🚀 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/DeNiS23208/jwt-auth-redis.git
cd jwt-auth-redis
```

### 2. Создание виртуального окружения

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Конфигурация переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Database
DATABASE_URL=postgresql+asyncpg://app_user:app_pass@localhost:5434/app_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

⚠️ **Для production:** Измените `SECRET_KEY` на криптографически стойкий ключ!

### 5. Запуск PostgreSQL и Redis

#### Вариант A: Docker Compose (рекомендуется)

```bash
docker-compose up -d
```

Это запустит:

- PostgreSQL на `localhost:5434`
- Redis на `localhost:6379`

#### Вариант B: Локально

```bash
# Запуск PostgreSQL
# macOS (если установлен через brew)
brew services start postgresql

# Запуск Redis
# macOS (если установлен через brew)
brew services start redis
```

### 6. Миграции БД (Alembic)

```bash
# Создание всех таблиц
alembic upgrade head
```

---

## ▶️ Запуск

### Локальный запуск (разработка)

```bash
uvicorn app.main:app --reload
```

Сервер будет доступен на: **http://localhost:8000**

### Swagger документация

API документация доступна на: **http://localhost:8000/docs**

### Проверка здоровья сервера

```bash
curl http://localhost:8000/
```

Ответ:

```json
{ "message": "API is working" }
```

---

## 📡 API Endpoints

### 🔐 Аутентификация (`/auth`)

#### Регистрация

```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "role_id": 1
}

# Ответ (201)
{
  "id": 1,
  "email": "user@example.com",
  "role_id": 1,
  "is_active": true
}
```

#### Вход

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

# Ответ (200)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Обновление токена

```bash
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Ответ (200)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Выход

```bash
POST /auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Ответ (200)
{
  "message": "Успешный выход из системы"
}
```

### 👤 Пользователь (`/users`)

#### Получение профиля текущего пользователя

```bash
GET /users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Ответ (200)
{
  "id": 1,
  "email": "user@example.com",
  "role_id": 1,
  "is_active": true
}
```

### 📄 Контент (`/content`)

#### Получение контента (с фильтром по роли)

```bash
GET /content
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Ответ (200)
[
  {
    "id": 1,
    "title": "Публичная статья",
    "body": "Доступна всем",
    "access_level": "common"
  },
  {
    "id": 2,
    "title": "Статья для role1",
    "body": "Доступна только role1",
    "access_level": "role1"
  }
]
```

**Фильтрация по ролям:**

- `access_level="common"` — доступна всем
- `access_level="role1"` — только пользователям с role_id=1
- `access_level="role2"` — только пользователям с role_id=2

---

## 💡 Использование

### Пример workflow: Полный цикл аутентификации

```bash
# 1️⃣ Регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "mypassword123",
    "role_id": 1
  }'

# 2️⃣ Вход (получение токенов)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "mypassword123"
  }'

# Сохраните access_token и refresh_token

# 3️⃣ Доступ к защищенному ресурсу
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4️⃣ Получение контента (с ролевым фильтром)
curl -X GET http://localhost:8000/content \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 5️⃣ Обновление токена (когда access истек)
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'

# 6️⃣ Выход из системы (инвалидация токена)
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔒 Безопасность

### JWT структура

Каждый JWT содержит:

```json
{
  "sub": "1", // ID пользователя
  "role": "role1", // Роль пользователя
  "type": "access", // Тип токена (access/refresh)
  "jti": "uuid-uuid", // Уникальный ID токена (для черного списка)
  "exp": 1234567890 // Время истечения
}
```

### Проверка безопасности токена

Каждый токен проверяется:

1. **Подпись** — валидна ли цифровая подпись (не подделан ли)
2. **Время истечения** — не истек ли токен
3. **Черный список** — не отозван ли токен при logout
4. **Белый список** — находится ли активный токен в системе

### Функции безопасности

- ✅ **Хеширование паролей** — bcrypt с солью
- ✅ **Асинхронная обработка** — защита от timing attacks
- ✅ **Инвалидация токенов** — мгновенное удаление при logout
- ✅ **Refresh токены** — разделение access/refresh для безопасности
- ✅ **JWT с jti** — защита от replay attacks

### 🚨 Рекомендации для Production

```env
# Измените эти значения:
SECRET_KEY=supersecretkey  # ❌ Плохо (слишком простой)
SECRET_KEY=your-128-character-cryptographically-secure-random-string-here-change-this  # ✅ Хорошо

# Увеличьте сложность:
ACCESS_TOKEN_EXPIRE_MINUTES=15    # Оставить или уменьшить до 5-10
REFRESH_TOKEN_EXPIRE_DAYS=7       # Оставить

# Используйте HTTPS
# Включите CORS только для доверенных доменов
# Добавьте rate limiting
# Включите логирование всех попыток доступа
```

### Известные уязвимости и как их минимизировать

| Уязвимость            | Описание                                       | Решение                                        |
| --------------------- | ---------------------------------------------- | ---------------------------------------------- |
| Token Theft           | XSS атаке может украсть токен из localStorage  | Использовать httpOnly cookies                  |
| Token Replay          | Украденный токен может быть использован        | Использовать jti + короткий TTL                |
| Weak Secret           | Слабый SECRET_KEY можно перебрать              | Использовать криптостойкий ключ (32+ символов) |
| No Refresh Validation | Refresh может выдавать новые access бесконечно | Добавить проверку refresh в Redis              |
| No Rate Limiting      | Brute force атаки на /login                    | Добавить rate limiting middleware              |

---

## 🐳 Docker

### Запуск с Docker Compose

```bash
# Запуск всех сервисов (PostgreSQL + Redis)
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f redis
docker-compose logs -f db
```

### Структура docker-compose

```yaml
services:
  db:
    image: postgres:15
    ports: 5434:5432
    volumes: postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports: 6379:6379
```

### Создание Docker образа FastAPI (TODO)

⚠️ **Dockerfile пока пустой.** Нужно создать:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📁 Структура проекта

```
jwt-auth-redis/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                 # Dependency injection
│   │   └── v1/
│   │       ├── auth.py             # Endpoints аутентификации
│   │       ├── users.py            # Endpoints профиля
│   │       └── content.py          # Endpoints контента
│   ├── core/
│   │   ├── config.py               # Конфигурация (settings)
│   │   ├── security.py             # JWT, хеширование пароль
│   │   └── redis.py                # Redis функции
│   ├── db/
│   │   ├── base.py                 # Base класс для моделей
│   │   ├── session.py              # SQLAlchemy конфигурация
│   │   └── models/
│   │       ├── user.py             # User модель
│   │       ├── role.py             # Role модель
│   │       └── content.py          # Content модель
│   ├── schemas/
│   │   ├── auth.py                 # Pydantic схемы авторизации
│   │   ├── user.py                 # Pydantic схемы пользователя
│   │   └── content.py              # Pydantic схемы контента
│   ├── services/
│   │   ├── auth_service.py         # Бизнес-логика аутентификации
│   │   ├── content_service.py      # Бизнес-логика контента
│   │   └── token_service.py        # (пусто, для расширения)
│   └── main.py                      # FastAPI приложение
├── alembic/                         # Миграции
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── docker-compose.yml               # Docker Compose конфиг
├── Dockerfile                       # (пуст, требуется заполнение)
├── requirements.txt                 # Python зависимости
├── .env                             # Переменные окружения
├── .gitignore
└── README.md                        # Этот файл
```

---

## 🔧 Разработка

### Запуск с автоперезагрузкой (hot reload)

```bash
uvicorn app.main:app --reload
```

### Создание новой миграции (Alembic)

```bash
# Автогенерация миграции на основе моделей
alembic revision --autogenerate -m "описание изменения"

# Применение миграции
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

### Тестирование API

Используйте **Swagger UI** на `http://localhost:8000/docs`

Или используйте **curl** / **Postman** / **REST Client**

---

## 📊 Примеры вывода

### Получение контента с фильтром по ролям

```bash
# User с role1
GET /content
Authorization: Bearer TOKEN_ROLE1

[
  { "id": 1, "title": "Публичная статья", "access_level": "common" },
  { "id": 2, "title": "Статья для role1", "access_level": "role1" }
]

# User с role2
GET /content
Authorization: Bearer TOKEN_ROLE2

[
  { "id": 1, "title": "Публичная статья", "access_level": "common" },
  { "id": 3, "title": "Статья для role2", "access_level": "role2" }
]
```

---

## 🐛 Troubleshooting

### "Connection refused" при подключении к Django

Убедитесь что PostgreSQL запущен:

```bash
docker-compose ps
# или
brew services list | grep postgres
```

### "Redis connection error"

Убедитесь что Redis запущен:

```bash
docker-compose ps
# или
brew services list | grep redis
```

### "Token не найден в белом списке"

Это означает:

- Токен был инвалидирован (logout)
- Сервис перезагружался (данные Redis потеряны)
- Токен истек

**Решение:** Выполните login заново

### "Неверный SECRET_KEY"

Если при запуске ошибка декодирования JWT:

```bash
# Проверьте что SECRET_KEY совпадает в коде и .env
# Перезаведитесь (старые токены станут невалидными)
```

---

## 📚 Дополнительные ресурсы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [JWT.io](https://jwt.io/)
- [Redis Documentation](https://redis.io/documentation)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 📝 Лицензия

Этот проект создан в образовательных целях.

---

## 👨‍💻 Автор

**DeNiS23208**  
GitHub: https://github.com/DeNiS23208/jwt-auth-redis

---

**Последнее обновление:** 17 апреля 2026  
**Версия:** 1.0.0
