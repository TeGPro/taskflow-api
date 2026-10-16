# TaskFlow API

**Версия Python:** `3.14.7`

---

## Быстрый старт

### 1. Создание и активация виртуального окружения

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Установка проекта

Установите проект из текущей директории:

```bash
python -m pip install . --group dev
```

### 3. Запуск приложения

Запустите сервер с помощью `uvicorn`:

```bash
uvicorn app.main:app --reload
```

### 4. Документация

После запуска сервера документация доступна по адресу:

```
http://127.0.0.1:8000/docs
```

---

## Проверка кода

Для проверки качества кода используйте `ruff`:

```bash
ruff check .
ruff format --check .
```