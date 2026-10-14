Аутентификация:
HTTP-метод | Путь | Тело запроса | Ответ | HTTP-код | Кто имеет право |
|---|---|---|---|---|---|
|POST| /api/v1/auth/register | email, password, display_name | id, email, display_name, created_at | 201 | Все
|POST| /api/v1/auth/login | email, password | access_token, token_type, expires_in | 200 | Все, без токена; успешный вход - при верных email и пароле
|GET| /api/v1/users/me | - | id, email, display_name, created_at | 200 | авторизованные пользователи

Проекты:
HTTP-метод | Путь | Тело запроса | Ответ | HTTP-код | Кто имеет право |
|---|---|---|---|---|---|
|POST|/api/v1/projects|name, description(не обязательно)|id, owner_id, created_at, updated_at, name, description|201|авторизованные пользователи|
|GET|/api/v1/projects|---|name, id, created_at, updated_at, description, owner_id всех доступных проектов|200|авторизованные пользователи|
|GET|/api/v1/projects/{project_id}|---|name, id, created_at, updated_at, description, owner_id|200|авторизованные пользователи с доступом к проекту|
|PATCH|/api/v1/projects/{project_id}|name и(или) description|name, id, created_at, updated_at, description, owner_id|200|owner проекта|
|DELETE|/api/v1/projects/{project_id}|---|Без тела ответа|204|owner проекта|
|GET|/api/v1/projects/{project_id}/members|---|список(user_id, email, display_name, role)|200|авторизованные пользователи с доступом к проекту|
|POST|/api/v1/projects/{project_id}/members|email, role(editor, viewer)|user_id, email, display_name, role|201|owner проекта|
|PATCH|/api/v1/projects/{project_id}/members/{user_id}|role|user_id, email, display_name, role|200|owner проекта|
|DELETE|/api/v1/projects/{project_id}/members/{user_id}|---|Без тела ответа|204|owner проекта|

Задачи:
HTTP-метод | Путь | Тело запроса | Ответ | HTTP-код | Кто имеет право |
|---|---|---|---|---|---|
|POST|/api/v1/projects/{project_id}/tasks|title, description(опционально),priority(опционально, по умолчанию medium), status(опционально, по умолчанию todo),assignee_id(опционально), due_at(опционально)|id, title, description,priority, status, assignee_id, due_at, project_id, created_by, created_at, updated_at|201|owner или editor проекта|
|GET|/api/v1/projects/{project_id}/tasks|---|items, total, limit, offset|200|авторизованные пользователи с доступом к проекту|
|GET|/api/v1/tasks/{task_id}|---|id, title, description,priority, status, assignee_id, due_at, project_id, created_by, created_at, updated_at|200|авторизованные пользователи с доступом к проекту|
|PATCH|/api/v1/tasks/{task_id}|status, priority, title, description, assignee_id, due_at (каждое поле передается по необходимости)|id, title, description,priority, status, assignee_id, due_at, project_id, created_by, created_at, updated_at|200|owner или editor проекта|
|DELETE|/api/v1/tasks/{task_id}|---|Без тела ответа|204|owner или editor проекта|

**Параметры URL**: status, priority, limit, offset, sort, order. Поле items содержит список задач.

Ошибки:
|Операция|Условие ошибки|HTTP-код|
|---|---|---|
|Запрос к закрытому эндпоинту|Отсутствие токена|401|
|Запрос к закрытому эндпоинту|Просроченный токен|401|
|Регистрация|email занят|409|
|Вход|Неверный пароль|401|
|Создание проекта|Пустой name|422|
|Изменение задачи|Пользователь обладает ролью viewer|403|
|Удаление проекта|Пользователь обладает ролью editor|403|
|Запрос проекта|Посторонний пользователь, известный UUID|404|
|Запрос задачи|Посторонний пользователь, несуществующий UUID|404|
|Добавление пользователя|пользователь уже состоит в проекте|409|