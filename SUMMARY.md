# Итоговая конфигурация доступа по IP и GitHub Pages

## ✅ Что было сделано

### 1. Созданы файлы конфигурации
- `frontend/.env.development` - для локальной разработки (использует прокси)
- `frontend/.env.production` - для GitHub Pages (прямой URL к бэкенду)
- `frontend/.env.example` - пример конфигурации

### 2. Обновлены основные файлы
- **`frontend/vite.config.ts`**:
  - Добавлен `host: '0.0.0.0'` для доступа по IP
  - Прокси настроен на `0.0.0.0:8005`
  - Используются переменные окружения

- **`frontend/src/drugsApi.ts`**:
  - API_BASE_URL берется из переменных окружения
  - Development: пустая строка (прокси через Vite)
  - Production: полный URL с IP

- **`frontend/package.json`**:
  - Добавлен скрипт `dev:ip` для явного указания host

- **`application/settings.py`**:
  - Уже настроен: `ALLOWED_HOSTS = ['*']`
  - Уже настроен: `CORS_ALLOW_ALL_ORIGINS = True`

### 3. Созданы скрипты автоматизации

#### `./run_backend.sh`
Запуск Django на `0.0.0.0:8005` с отображением IP

#### `./run_frontend.sh`
Запуск React на `0.0.0.0:3005` с отображением IP

#### `./setup_ip_for_ghpages.sh`
Автоматическая настройка IP в `.env.production`

#### `./deploy_to_ghpages.sh`
Полный цикл деплоя: настройка IP → сборка → деплой

#### `./check_config.sh`
Проверка конфигурации и статуса системы

### 4. Создана документация
- **`SETUP_IP_ACCESS.md`** - полная инструкция
- **`QUICK_REFERENCE.md`** - быстрая шпаргалка
- **`SUMMARY.md`** - этот файл

## 🎯 Как это работает

### Локальная разработка (Development)

```
┌─────────────────┐
│   Браузер       │
│  localhost:3005 │ или 192.168.1.XXX:3005
└────────┬────────┘
         │
         │ fetch('/api/...')
         ↓
┌─────────────────┐
│   Vite Dev      │
│   port 3005     │
│   host 0.0.0.0  │
└────────┬────────┘
         │
         │ Proxy /api → http://0.0.0.0:8005
         ↓
┌─────────────────┐
│   Django        │
│   port 8005     │
│   host 0.0.0.0  │
└─────────────────┘
```

**Особенности:**
- API_BASE_URL = '' (пустая строка)
- Все запросы `/api/*` проксируются через Vite
- Работает и по localhost, и по IP

### Production (GitHub Pages)

```
┌─────────────────────┐
│   Браузер           │
│  github.io/...      │
└──────────┬──────────┘
           │
           │ Загружает статику (HTML/JS/CSS)
           ↓
┌─────────────────────┐
│  GitHub Pages       │
│  (CDN)              │
└─────────────────────┘

Затем браузер делает запросы:

┌─────────────────────┐
│   Браузер           │
└──────────┬──────────┘
           │
           │ fetch('http://192.168.1.XXX:8005/api/...')
           ↓
┌─────────────────────┐
│   Django (локально) │
│   192.168.1.XXX     │
│   port 8005         │
└─────────────────────┘
```

**Особенности:**
- API_BASE_URL = 'http://192.168.1.XXX:8005'
- Запросы идут напрямую на локальный сервер
- Работает только в одной WiFi сети

## 📋 Сценарии использования

### Сценарий 1: Разработка на локальной машине
```bash
# Терминал 1
./run_backend.sh

# Терминал 2
./run_frontend.sh

# Открыть в браузере
http://localhost:3005
```

### Сценарий 2: Тестирование с телефона в локальной сети
```bash
# На компьютере
./run_backend.sh
./run_frontend.sh

# Смотрим IP (будет показан при запуске)
# Например: 192.168.1.240

# На телефоне открываем браузер
http://192.168.1.240:3005
```

### Сценарий 3: Деплой на GitHub Pages
```bash
# Автоматический способ
./deploy_to_ghpages.sh

# Или вручную
./setup_ip_for_ghpages.sh
cd frontend
npm run build
npm run deploy

# Не забыть запустить бэкенд
./run_backend.sh

# Открыть на любом устройстве в той же WiFi
https://YurchenkoK.github.io/vasoactive_drug_speed_estimatior_frontend/
```

## 🔍 Переменные окружения

### Development (.env.development)
```env
VITE_API_BASE_URL=
VITE_BACKEND_HOST=0.0.0.0
VITE_BACKEND_PORT=8005
```

### Production (.env.production)
```env
VITE_API_BASE_URL=http://192.168.1.240:8005
```

**Важно:** IP в `.env.production` должен совпадать с реальным IP вашей машины!

## 🧪 Проверка работы

### Проверить конфигурацию
```bash
./check_config.sh
```

### Проверить доступность бэкенда
```bash
# С локальной машины
curl http://localhost:8005/api/drugs/

# С другого устройства
curl http://192.168.1.XXX:8005/api/drugs/
```

### Проверить доступность фронтенда
```bash
# Открыть в браузере
http://192.168.1.XXX:3005
```

## ⚠️ Важные замечания

1. **Безопасность**: Текущая конфигурация (`CORS_ALLOW_ALL_ORIGINS = True`) подходит только для разработки!

2. **IP адрес**: В `.env.production` должен быть указан реальный IP вашей машины в локальной сети

3. **WiFi сеть**: Устройства должны быть подключены к одной WiFi сети

4. **Firewall**: Убедитесь, что порты 3005 и 8005 не заблокированы

5. **Docker**: Если вы работаете в Docker контейнере (как сейчас), нужно пробросить порты:
   ```bash
   docker run -p 8005:8005 -p 3005:3005 ...
   ```

## 📂 Структура файлов

```
/root/RIP/
├── run_backend.sh              # Запуск Django на 0.0.0.0
├── run_frontend.sh             # Запуск React на 0.0.0.0
├── setup_ip_for_ghpages.sh     # Настройка IP для GH Pages
├── deploy_to_ghpages.sh        # Полный деплой
├── check_config.sh             # Проверка конфигурации
├── SETUP_IP_ACCESS.md          # Полная документация
├── QUICK_REFERENCE.md          # Быстрая шпаргалка
└── SUMMARY.md                  # Этот файл

frontend/
├── .env.development            # Конфиг для development
├── .env.production             # Конфиг для production
├── .env.example                # Пример конфига
├── vite.config.ts              # Настройки Vite (обновлен)
├── package.json                # npm скрипты (обновлен)
└── src/
    └── drugsApi.ts             # API клиент (обновлен)

application/
└── settings.py                 # Django настройки (уже был готов)
```

## 🎓 Что нужно понять

1. **Development vs Production**:
   - Dev: прокси через Vite → нет проблем с CORS
   - Prod: прямые запросы → нужен правильный CORS

2. **localhost vs 0.0.0.0**:
   - `127.0.0.1/localhost` - только локальная машина
   - `0.0.0.0` - все сетевые интерфейсы (можно по IP)

3. **GitHub Pages ≠ Backend хостинг**:
   - GH Pages - только статика (HTML/JS/CSS)
   - Backend нужно хостить отдельно
   - Или использовать локальный backend в той же сети

4. **Прокси в Vite**:
   - Только в development режиме
   - В production не работает
   - Поэтому нужен API_BASE_URL

## ✅ Checklist перед использованием

- [ ] Установлены зависимости: `cd frontend && npm install`
- [ ] Настроен IP в `.env.production`: `./setup_ip_for_ghpages.sh`
- [ ] Запущен бэкенд на 0.0.0.0: `./run_backend.sh`
- [ ] Устройства в одной WiFi сети
- [ ] Firewall не блокирует порты 3005, 8005
- [ ] Проверена конфигурация: `./check_config.sh`

## 🚀 Быстрый старт

```bash
# 1. Проверка
./check_config.sh

# 2. Локальная разработка
./run_backend.sh &
./run_frontend.sh

# 3. Деплой на GitHub Pages
./deploy_to_ghpages.sh
```

Готово! 🎉
