# Инструкция по тестированию ЛР8 - Асинхронный сервис

## Архитектура решения

1. **Django сервис** (порт 8000) - основной веб-сервис с API для управления заявками
2. **Go сервис** (порт 8081) - асинхронный сервис для расчета скорости введения препаратов
3. **Межсервисное взаимодействие**:
   - Django → Go: POST запрос `/drugs_process/` при утверждении (complete) заявки
   - Go → Django: POST запрос `/api/orders/async/update_results/` с результатами после расчета (5-10 сек)

## Что было реализовано

### 1. Модель данных (models.py)
- Добавлено поле `async_calculation_result` в модель `DrugInOrder`
- Поле хранит результат асинхронного расчета скорости введения препарата

### 2. API эндпоинты Django

#### GET /api/orders/
Получение списка заявок с подсчетом заполненных результатов
```json
{
  "async_results_count": 2  // количество препаратов с заполненным результатом
}
```

#### PUT /api/orders/{id}/form/
Формирование заявки (переводит в статус FORMED)

#### PUT /api/orders/{id}/complete/
**Утверждение заявки модератором** - запускает асинхронные расчеты для всех препаратов в заявке.
После утверждения Django-сервис направляет POST запрос `/drugs_process/` в асинхронный Go-сервис.

#### POST /api/orders/async/update_results/
Принять результат от асинхронного сервиса (вызывается Go сервисом)
```json
{
  "secret_key": "a1b2c3d4e5f6g7h8",
  "order_id": 1,
  "results": [
    {
      "druginorder_id": 1,
      "infusion_speed": 2.5
    }
  ]
}
```

### 3. Go сервис

#### POST /drugs_process/
Запуск асинхронного расчета скорости введения препаратов.
Go-сервис принимает задачу, помещает её в очередь и возвращает ответ **202 Accepted**.
```json
{
  "order_id": 1,
  "drugs": [
    {
      "druginorder_id": 1,
      "drug_concentration": 4.0,
      "ampoule_volume": 5.0,
      "ampoules_count": 5,
      "solvent_volume": 100.0,
      "patient_weight": 70.0
    }
  ]
}
```

Ответ:
```json
{
  "status": "accepted",
  "message": "Задача помещена в очередь на обработку",
  "order_id": 1,
  "drugs_count": 1
}
```

#### GET /health
Проверка состояния сервиса

### 4. Авторизация
- Секретный ключ: `a1b2c3d4e5f6g7h8`
- Проверяется в эндпоинте `/api/orders/async/update_results/`

## Порядок тестирования через Insomnia

### Шаг 1: Авторизация
```
POST http://localhost:8000/api/users/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

### Шаг 2: Создание черновика заявки
```
POST http://localhost:8000/api/orders/cart/
Content-Type: application/json
Cookie: sessionid=<ваш_session_id>

{
  "ampoules_count": 5,
  "solvent_volume": 100,
  "patient_weight": 70
}
```
Запомните `order_id` из ответа.

### Шаг 3: Добавление препаратов в заявку
```
POST http://localhost:8000/api/drugs/1/add-to-order/
Content-Type: application/json
Cookie: sessionid=<ваш_session_id>

{
  "order_id": <order_id>,
  "ampoule_volume": 5.0
}
```

### Шаг 4: Получение списка заявок (до формирования)
```
GET http://localhost:8000/api/orders/
Cookie: sessionid=<ваш_session_id>
```
Проверьте, что `async_results_count: 0`

### Шаг 5: Формирование заявки
```
PUT http://localhost:8000/api/orders/<order_id>/form/
Cookie: sessionid=<ваш_session_id>
```
Заявка переходит в статус FORMED.

### Шаг 6: Утверждение заявки модератором (запуск асинхронного процесса)
```
PUT http://localhost:8000/api/orders/<order_id>/complete/
Cookie: sessionid=<ваш_session_id>
```
**После утверждения** Django-сервис направляет POST запрос `/drugs_process/` в асинхронный Go-сервис.
Go-сервис принимает задачу, помещает её в очередь и возвращает ответ **202 Accepted**.

### Шаг 7: Проверка Go сервиса (опционально)
```
POST http://localhost:8081/drugs_process/
Content-Type: application/json

{
  "order_id": 1,
  "drugs": [...]
}
```

### Шаг 8: Ожидание и проверка результата
Подождите 5-10 секунд, затем:
```
GET http://localhost:8000/api/orders/
Cookie: sessionid=<ваш_session_id>
```
Проверьте, что `async_results_count` увеличился!

### Шаг 9: Просмотр детальной информации о заявке
```
GET http://localhost:8000/api/orders/<order_id>/
Cookie: sessionid=<ваш_session_id>
```

### Шаг 10: Получение препаратов в заявке
```
GET http://localhost:8000/api/orders/<order_id>/drugs/<drug_id>/
Cookie: sessionid=<ваш_session_id>
```
Проверьте поле `async_calculation_result` - должно содержать результат типа:
- "Рассчитано асинхронно: 2.5 мг/кг/час"
- "Рассчитано асинхронно: 3.14 мг/кг/час"

### Шаг 11: Прямой вызов обновления результатов (с секретным ключом)
```
POST http://localhost:8000/api/orders/async/update_results/
Content-Type: application/json

{
  "secret_key": "a1b2c3d4e5f6g7h8",
  "order_id": 1,
  "results": [
    {
      "druginorder_id": 1,
      "infusion_speed": 99.99
    }
  ]
}
```

## Проверка асинхронности

1. **Сформируйте заявку** с несколькими препаратами (статус FORMED)
2. **Утвердите заявку** модератором (complete) → запустится асинхронная обработка
3. **Сразу получите** GET список заявок - `async_results_count: 0`
4. **Подождите 5-10 секунд**
5. **Снова получите** GET список заявок - `async_results_count` должен увеличиться!

## Логи Go сервиса

При работе Go сервис выводит:
```
→ Начат расчет для заявки ID: 1 (2 препаратов)
  Задержка: 7s
  ✓ Препарат 1: скорость введения = 2.86 мг/кг/час
  ✓ Препарат 2: скорость введения = 0.11 мг/кг/час
✓ Результаты отправлены для заявки ID: 1 (2 препаратов)
```

## Ожидаемые результаты

1. ✅ Заявка утверждается мгновенно (не ждет расчета)
2. ✅ Go сервис возвращает 202 Accepted
3. ✅ Расчет выполняется в фоне с задержкой 5-10 сек
4. ✅ Результаты постепенно появляются в БД
5. ✅ `async_results_count` увеличивается по мере готовности результатов
6. ✅ Секретный ключ защищает эндпоинт обновления результатов

## Диаграммы для РПЗ

### Последовательность действий (шаги 19–24):
1. Пользователь → Django: создать заявку (DRAFT)
2. Пользователь → Django: добавить препараты
3. Пользователь → Django: сформировать заявку (FORMED)
4. Модератор → Django: утвердить заявку (COMPLETED)
5. Django → Go: POST /drugs_process/ (асинхронная обработка)
6. Go → Django: 202 Accepted (задача помещена в очередь)
7. Go: расчет скорости введения 5-10 сек
8. Go → Django: POST /api/orders/async/update_results/ (с секретным ключом)
9. Django: проверяет ключ, обновляет данные заявки
10. Django → Go: 200 OK
11. Пользователь → Django: GET список заявок (видит результаты)

## Состояния заявки
- DRAFT → FORMED → COMPLETED
- DRAFT → FORMED → REJECTED
- DRAFT → DELETED
