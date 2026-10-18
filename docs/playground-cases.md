| Метод и путь | Вход | Ожидаемый выход | HTTP-статус | Причина |
|---|---|---|---|---|
| POST `/playground/tasks` | `{"title":"Изучить API","status":"todo"}` | Объект задачи: сгенерированный `id`, переданные `title` и `status` | 201 Created | Задача успешно создана |
| POST `/playground/tasks` | `{"status":"todo"}` | Ошибка валидации с указанием отсутствующего поля `title` | 422 Unprocessable Content | Обязательное поле `title` не передано |
| POST `/playground/tasks` | `{"title":"Изучить API","status":"blocked"}` | Ошибка валидации поля `status` | 422 Unprocessable Content | Допустимы только `todo`, `in_progress`, `done` |
| GET `/playground/tasks/{task_id}` | UUID ранее созданной задачи в пути; без тела | Объект найденной задачи: `id`, `title`, `status` | 200 OK | Задача найдена в хранилище |
| GET `/playground/tasks/{task_id}` | Корректный UUID отсутствующей задачи в пути; без тела | `{"detail":"Task not found"}` | 404 Not Found | UUID прошёл валидацию, но такой задачи в хранилище нет |
| GET `/playground/tasks?status=todo` | Query-параметр `status=todo`; без тела | Список задач со статусом `todo`; при отсутствии совпадений — `[]` | 200 OK | Запрос выполнен успешно; пустой результат фильтрации не является ошибкой |