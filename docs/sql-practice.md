## Оглавление

- [1. Создание таблиц](#1-создание-таблиц)
- [2. Просмотр таблиц](#2-просмотр-таблиц)
- [3. Тестовые данные](#3-тестовые-данные)
- [4. Проверки данных](#4-проверки-данных)
- [5. Пять запросов для примера](#5-пять-запросов-для-примера)
- [6. Проверка ограничений](#6-проверка-ограничений)
- [7. Транзакция и откат](#7-транзакция-и-откат)
- [8. EXPLAIN до и после индекса](#8-explain-до-и-после-индекса)

---

## 1. Создание таблиц

### `users`

```sql
create table users (
    id UUID primary key,
    email VARCHAR(255) unique not null,
    display_name VARCHAR(80) not null,
    password_hash text not null,
    created_at TIMESTAMP with time zone not null default now()
);
```

### `projects`

```sql
create table projects (
    id UUID primary key,
    owner_id UUID not null,
    foreign key (owner_id) references users(id),
    name VARCHAR(120) not null,
    description TEXT,
    created_at TIMESTAMP with time zone not null default now(),
    updated_at TIMESTAMP with time zone not null default now()
);
```

### `project_members`

```sql
create table project_members (
    project_id UUID,
    user_id UUID,
    primary key (project_id, user_id),
    foreign key (project_id) references projects(id) on delete cascade,
    foreign key (user_id) references users(id),
    role varchar(20) not null check (role in ('editor','viewer')),
    joined_at TIMESTAMP with time zone not null default now()
);
```

### `tasks`

```sql
create table tasks (
    id UUID primary key,
    project_id UUID not null,
    foreign key (project_id) references projects(id) on delete cascade,
    created_by UUID not null,
    foreign key (created_by) references users(id),
    assignee_id UUID,
    foreign key (assignee_id) references users(id),
    title VARCHAR(160) not null,
    description TEXT,
    status varchar(20) not null check (status in ('todo','in_progress', 'done')) default 'todo',
    priority varchar(20) not null check (priority in ('low','medium', 'high')) default 'medium',
    due_at TIMESTAMP with time zone,
    created_at TIMESTAMP with time zone not null default now(),
    updated_at TIMESTAMP with time zone not null default now()
);
```

## 2. Просмотр таблиц

`# --`

```sql
select *
from users;

select *
from projects;

select *
from project_members;

select *
from tasks;
```

## 3. Тестовые данные

```sql
--Далее внесем тестовые данные в таблицы
```

### Пользователи

```sql
insert into users (id, email, display_name, password_hash)
values
    ('a7d3c920-6b14-4e85-9f02-13c8d6a5b741', 'alice@example.com', 'Alice', 'training_hash_alice'),
    ('42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5', 'boris@example.com', 'Boris', 'training_hash_boris'),
    ('d19f604a-82e7-4b35-8c91-f0a6d2e743b8', 'vera@example.com', 'Vera', 'training_hash_vera'),
    ('6e2a9b13-f584-40c7-bd62-8a3175e9c046', 'denis@example.com', 'Denis', 'training_hash_denis');
```

### Проекты

```sql
insert into projects (id, owner_id, name, description)
values
    ('b5037d8e-19a2-46f0-97c4-2e6b8a01d935', 'a7d3c920-6b14-4e85-9f02-13c8d6a5b741','Учебная платформа','Здесь какой-то текст, касающийся Учебной платформы'),
    ('0c8f52a7-d631-4b9e-a074-5f2d18c6e3b9', '42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5','База данных','Базы данных это ...');
```

### Участники проектов

```sql
insert into project_members (project_id, user_id, role)
values
    ('b5037d8e-19a2-46f0-97c4-2e6b8a01d935','42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5','editor'),
    ('b5037d8e-19a2-46f0-97c4-2e6b8a01d935','d19f604a-82e7-4b35-8c91-f0a6d2e743b8','viewer');
```

### Задачи

```sql
insert into tasks (id, project_id, created_by, title, status, assignee_id)
values
    ('f26b1e94-7a03-45d8-8e62-c901b4a73f50','b5037d8e-19a2-46f0-97c4-2e6b8a01d935','a7d3c920-6b14-4e85-9f02-13c8d6a5b741','Спроектировать БД', 'done', '42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5'),
    ('93a0d6c5-e218-4f72-b639-7d5a02e8c146','b5037d8e-19a2-46f0-97c4-2e6b8a01d935','a7d3c920-6b14-4e85-9f02-13c8d6a5b741','Создать API', 'in_progress', NULL),
    ('5b71e3a9-c460-48fd-9157-e2a806d3b924','b5037d8e-19a2-46f0-97c4-2e6b8a01d935','a7d3c920-6b14-4e85-9f02-13c8d6a5b741','Написать тесты', 'todo', 'a7d3c920-6b14-4e85-9f02-13c8d6a5b741'),
    ('e0842c6f-35b9-41a0-a8d3-64f7c192e50b','0c8f52a7-d631-4b9e-a074-5f2d18c6e3b9','42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5','Нарисовать ER-диаграмму', 'in_progress', '42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5');
```

## 4. Проверки данных

```sql
--Проверки данных

select id, email, display_name, created_at
from users;

select id, owner_id, name, description
from projects;

select project_id, user_id, role
from project_members;

select id, project_id, created_by, title, status, assignee_id
from tasks;
```

## 5. Пять запросов для примера

```sql
--Теперь напишем пять запросов для примера
```

### 5.1. Все проекты Алисы

```sql
--Все проекты Алисы
select *
from projects inner join users
on projects.owner_id = users.id
where users.email = 'alice@example.com';
```

### 5.2. Задачи todo для проектов Алисы

```sql
--Задачи todo для проектов Алисы
select tasks.*
from tasks
inner join projects
on tasks.project_id = projects.id
inner join users
on projects.owner_id = users.id
where users.email = 'alice@example.com' and tasks.status = 'todo';
```

### 5.3. Количество задач по статусу

```sql
--Количество задач по статусу
select status, count(*) as status_count
from tasks
group by status;
```

### 5.4. Задача + имя исполнителя

```sql
--Задача + имя исполнителя
select title, users.display_name
from tasks left join users
on tasks.assignee_id = users.id;
```

### 5.5. Все проекты Бориса, включая членство

```sql
--Все проекты Бориса, включая членство
select distinct projects.*
from projects left join project_members
on projects.id = project_members.project_id
where owner_id = '42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5' or user_id = '42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5';
```

## 6. Проверка ограничений

```sql
--Теперь проверим ограничения
```

### 6.1. Существующий email

```sql
--Добавим нового пользователя с существующим email

insert into users (id, email, display_name, password_hash)
values
    ('7c921e4a-8d63-4b10-a592-f6e03c847d21', 'alice@example.com', 'Bobik', 'training_hash_bobik');
--Ошибка появилась, всё хорошо
```

### 6.2. Несуществующий project_id

```sql
--Добавим задачу с новым id и с несуществующим project_id, остальные поля корректные
insert into tasks (id, project_id, created_by, title, status, assignee_id)
values
    ('7c921e4a-8d63-4b10-a592-f6e03c847d21','e5b084d3-26a9-47fc-9318-0d7a62c5b490','a7d3c920-6b14-4e85-9f02-13c8d6a5b741','Что-то там', 'todo', '42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5');
--Ошибка появилась, всё хорошо
```

### 6.3. Недопустимый статус

```sql
--Последняя проверка - check, попробуем добавить задачу со статусом other
insert into tasks (id, project_id, created_by, title, status, assignee_id)
values
    ('31f6a8c2-b507-4d9e-86a4-c9207e13f5bd','b5037d8e-19a2-46f0-97c4-2e6b8a01d935','a7d3c920-6b14-4e85-9f02-13c8d6a5b741','Придумать архитектуру приложения', 'other', '42b8e1f6-0c93-47ad-a518-9d2f6c03e8b5')
--Ошибка появилась, всё хорошо
```

## 7. Транзакция и откат

```sql
-- Теперь попробуем сделать транзакцию, в которой поменяем статус первой задачи

-- Посмотрим исходный статус
select title, status
from tasks
where id = 'f26b1e94-7a03-45d8-8e62-c901b4a73f50';

-- Начинаем транзакцию
begin;
update tasks
set status = 'todo'
where id = 'f26b1e94-7a03-45d8-8e62-c901b4a73f50';
--делаем ролбэк и смотрим
rollback;
-- все получилось
```

## 8. EXPLAIN до и после индекса

```sql
-- далее нужно сравнить EXPLAIN до и после индекса на tasks.project_id
```

### 8.1. До индекса

```sql
-- до индекса
EXPLAIN
select *
from tasks
where tasks.project_id = 'b5037d8e-19a2-46f0-97c4-2e6b8a01d935';
-- Сейчас у нас Seq Scan on tasks  (cost=0.00..11.62 rows=1 width=574)
```

### 8.2. Создание индекса

```sql
-- Теперь сделаем индекс по project_id
create index ix_tasks_project_id
on tasks (project_id);
```

### 8.3. После индекса

```sql
-- Теперь еще раз посмотрим explain, уже после индекса
EXPLAIN
select *
from tasks
where tasks.project_id = 'b5037d8e-19a2-46f0-97c4-2e6b8a01d935';
-- Получилось Seq Scan on tasks  (cost=0.00..1.05 rows=1 width=574)
```

---

> -- На этом все эксперименты завершены.