# 🎬 Примеры использования

## Сценарий 1: Первое использование

```bash
# Шаг 1: Клонирование репозитория (если еще не сделано)
git clone <repository-url>
cd vasoactive_drug_speed_estimatior_async

# Шаг 2: Установка зависимостей
cd frontend
npm install
cd ..

# Шаг 3: Проверка конфигурации
./check_config.sh

# Результат:
# ✅ IP адрес: 192.168.1.240
# ⚠️  Порт 8000 свободен (запустите бэкенд)
# ⚠️  Порт 3000 свободен (запустите фронтенд)
# ✅ frontend/.env.development существует
# ...

# Шаг 4: Запуск приложения
# Терминал 1:
./run_backend.sh

# Терминал 2:
./run_frontend.sh

# Шаг 5: Открыть в браузере
# http://localhost:3000
```

## Сценарий 2: Разработка с телефона

```bash
# На компьютере:

# Терминал 1: Запускаем бэкенд
./run_backend.sh
# Выводит:
# ═══════════════════════════════════════
# Запуск Django на 0.0.0.0:8000...
# Ваш IP в локальной сети: 192.168.1.240
# Подключайтесь по адресу: http://192.168.1.240:8000
# ═══════════════════════════════════════

# Терминал 2: Запускаем фронтенд
./run_frontend.sh
# Выводит:
# ═══════════════════════════════════════
# Запуск фронтенда на 0.0.0.0:3000...
# Ваш IP в локальной сети: 192.168.1.240
# Подключайтесь по адресу: http://192.168.1.240:3000
# ═══════════════════════════════════════

# На телефоне:
# 1. Подключиться к той же WiFi сети
# 2. Открыть браузер
# 3. Ввести: http://192.168.1.240:3000
# 4. Приложение работает полностью!
```

## Сценарий 3: Первый деплой на GitHub Pages

```bash
# Шаг 1: Настройка IP для production
./setup_ip_for_ghpages.sh

# Интерактивный вывод:
# === Настройка IP для GitHub Pages ===
# 
# ✅ Ваш IP адрес: 192.168.1.240
# 
# ✅ Файл .env.production обновлен
# 
# Содержимое:
# # Автоматически сгенерировано Fri Dec 13 05:26:00 UTC 2025
# # IP адрес для GitHub Pages
# VITE_API_BASE_URL=http://192.168.1.240:8000
# 
# ──────────────────────────────────────
# Теперь можно деплоить на GitHub Pages:
#   cd frontend
#   npm run build
#   npm run deploy
# ──────────────────────────────────────

# Шаг 2: Запуск бэкенда (ВАЖНО!)
./run_backend.sh

# Шаг 3: Сборка и деплой
cd frontend
npm run build
npm run deploy

# Шаг 4: Открыть GitHub Pages
# https://YurchenkoK.github.io/vasoactive_drug_speed_estimatior_frontend/

# Готово! Приложение работает с локальным бэкендом
```

## Сценарий 4: Автоматический деплой

```bash
# Один скрипт делает все:
./deploy_to_ghpages.sh

# Вывод:
# ╔═══════════════════════════════════════════════════╗
# ║  Деплой на GitHub Pages с локальным бэкендом     ║
# ╚═══════════════════════════════════════════════════╝
# 
# 📍 Шаг 1: Настройка IP адреса...
# === Настройка IP для GitHub Pages ===
# ✅ Ваш IP адрес: 192.168.1.240
# ✅ Файл .env.production обновлен
# 
# Продолжить деплой? (y/n): y
# 
# 🔨 Шаг 2: Сборка приложения...
# [сборка...]
# 
# 🚀 Шаг 3: Деплой на GitHub Pages...
# [деплой...]
# 
# ╔═══════════════════════════════════════════════════╗
# ║  ✅ Деплой завершен успешно!                     ║
# ╚═══════════════════════════════════════════════════╝
# 
# 📝 Не забудьте:
#   1. Запустить бэкенд: ./run_backend.sh
#   2. Убедиться, что устройство в той же WiFi сети
# 
# 🌐 Ваше приложение:
#   https://YurchenkoK.github.io/vasoactive_drug_speed_estimatior_frontend/
```

## Сценарий 5: Отладка проблем

```bash
# Что-то не работает? Проверяем конфигурацию:
./check_config.sh

# Вывод покажет все проблемы:
# ╔══════════════════════════════════════════════════╗
# ║  Проверка конфигурации IP доступа                ║
# ╚══════════════════════════════════════════════════╝
# 
# 📍 1. Проверка IP адреса...
#    ✅ IP адрес: 192.168.1.240
# 
# 🔌 2. Проверка доступности портов...
#    ⚠️  Порт 8000 свободен (запустите бэкенд)  ← ПРОБЛЕМА!
#    ✅ Порт 3000 (Vite) занят
# 
# 📝 3. Проверка файлов конфигурации...
#    ✅ frontend/.env.development существует
#    ⚠️  frontend/.env.production не найден     ← ПРОБЛЕМА!
# 
# 🔧 4. Проверка Django settings...
#    ✅ CORS_ALLOW_ALL_ORIGINS = True
#    ✅ ALLOWED_HOSTS настроен для всех хостов

# Решение проблем:
# 1. Запустить бэкенд:
./run_backend.sh

# 2. Настроить production конфиг:
./setup_ip_for_ghpages.sh
```

## Сценарий 6: Смена IP адреса

```bash
# Если вы подключились к другой WiFi сети и IP изменился:

# Шаг 1: Проверить новый IP
./check_config.sh
# Покажет новый IP, например: 192.168.88.15

# Шаг 2: Обновить production конфиг
./setup_ip_for_ghpages.sh
# Автоматически обновит .env.production с новым IP

# Шаг 3: Пересобрать и задеплоить
cd frontend
npm run build
npm run deploy

# Готово! GitHub Pages теперь использует новый IP
```

## Сценарий 7: Работа в команде

```bash
# Разработчик 1 (бэкенд):
./run_backend.sh
# Запускает: http://192.168.1.240:8000
# Говорит команде: "Бэк на 192.168.1.240:8000"

# Разработчик 2 (фронтенд):
# В своем терминале:
cd frontend

# Редактирует .env.development:
echo "VITE_BACKEND_HOST=192.168.1.240" >> .env.development

# Запускает фронтенд:
npm run dev

# Теперь фронтенд разработчика подключается к бэку первого!
```

## Сценарий 8: Демонстрация преподавателю

```bash
# Подготовка:
./check_config.sh          # Проверка
./run_backend.sh &         # Бэкенд в фоне
./run_frontend.sh          # Фронтенд

# Демонстрация 1: Локальный доступ
# Браузер: http://localhost:3000
# Показать работу приложения

# Демонстрация 2: Доступ по IP
# Взять телефон, открыть: http://192.168.1.240:3000
# Показать, что работает точно так же

# Демонстрация 3: GitHub Pages
# Открыть: https://YurchenkoK.github.io/vasoactive_drug_speed_estimatior_frontend/
# Показать, что делает запросы к локальному бэку
# Открыть DevTools → Network → показать запросы к 192.168.1.240:8000

# Демонстрация 4: Документация
cat VISUAL_GUIDE.txt       # Показать визуальное руководство
```

## Сценарий 9: Тестирование API

```bash
# Запустить бэкенд:
./run_backend.sh

# В другом терминале:

# Тест 1: Локальный запрос
curl http://localhost:8000/api/drugs/ | jq

# Тест 2: Запрос по IP
curl http://192.168.1.240:8000/api/drugs/ | jq

# Тест 3: С другого устройства (телефон/планшет)
# Установить termux или использовать браузер DevTools:
fetch('http://192.168.1.240:8000/api/drugs/')
  .then(r => r.json())
  .then(console.log)
```

## Сценарий 10: Production-ready деплой

```bash
# ВНИМАНИЕ: Для настоящего production нужно больше настроек!

# Шаг 1: Обновить settings.py для production
# Вместо:
CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['*']

# Использовать:
CORS_ALLOWED_ORIGINS = [
    'https://yourchenkok.github.io',
]
ALLOWED_HOSTS = ['your-domain.com', '192.168.1.240']
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

# Шаг 2: Использовать HTTPS
# Настроить nginx + certbot для SSL

# Шаг 3: Деплой на сервер (не локально)
# Использовать VPS, Heroku, или подобное

# Шаг 4: Обновить .env.production
VITE_API_BASE_URL=https://your-api-domain.com

# Шаг 5: Деплой
./deploy_to_ghpages.sh
```

## Полезные команды

```bash
# Просмотр документации
cat VISUAL_GUIDE.txt          # Визуальное руководство
cat QUICK_REFERENCE.md         # Быстрая шпаргалка
cat SETUP_IP_ACCESS.md         # Подробная инструкция
cat INSTRUCTOR_GUIDE.md        # Для преподавателя

# Проверка статуса
./check_config.sh              # Полная проверка
netstat -tuln | grep 8000      # Проверить бэкенд
netstat -tuln | grep 3000      # Проверить фронтенд
ip addr show                   # Показать IP

# Логи
./run_backend.sh | tee backend.log    # Логи бэкенда
./run_frontend.sh | tee frontend.log  # Логи фронтенда

# Остановка
pkill -f "manage.py runserver"        # Остановить Django
pkill -f "vite"                       # Остановить Vite
```

## Tips & Tricks

### Tip 1: Быстрое переключение между режимами
```bash
# Development (с проксированием):
cd frontend
npm run dev

# Production build (прямые запросы):
npm run build
npm run preview  # Превью production сборки локально
```

### Tip 2: Использование разных портов
```bash
# Если порт 3000 занят:
cd frontend
vite --port 3001 --host 0.0.0.0

# Если порт 8000 занят:
python manage.py runserver 0.0.0.0:8001
```

### Tip 3: Отладка CORS
```bash
# Проверить CORS headers:
curl -I -X OPTIONS \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  http://192.168.1.240:8000/api/drugs/

# Должны быть headers:
# Access-Control-Allow-Origin: *
# Access-Control-Allow-Credentials: true
```

### Tip 4: Мониторинг запросов
```bash
# В браузере DevTools:
# Network → фильтр XHR → смотрим API запросы

# Или использовать расширение:
# - Chrome: "React Developer Tools"
# - Firefox: "Redux DevTools"
```
