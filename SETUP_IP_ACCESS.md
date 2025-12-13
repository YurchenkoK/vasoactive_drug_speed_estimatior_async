# Настройка доступа по IP и работа с GitHub Pages

## Проблема
Необходимо обеспечить:
1. Доступ к фронтенду и бэкенду по IP адресу из локальной сети (например, с телефона)
2. Работу GitHub Pages с локально запущенным бэкендом

## Решение

### 1. Локальная разработка (Development)

#### Запуск бэкенда (Django)
```bash
./run_backend.sh
# или
python manage.py runserver 0.0.0.0:8000
```

Сервер будет доступен:
- `http://localhost:8000` - с локальной машины
- `http://192.168.1.XXX:8000` - из локальной сети (WiFi)

#### Запуск фронтенда (React)
```bash
./run_frontend.sh
# или
cd frontend && npm run dev
```

Фронтенд будет доступен:
- `http://localhost:3000` - с локальной машины
- `http://192.168.1.XXX:3000` - из локальной сети (WiFi)

**В режиме разработки:**
- Все запросы `/api/*` проксируются на бэкенд через Vite
- Не нужно указывать полный URL бэкенда

### 2. Production (GitHub Pages)

#### Настройка перед деплоем

1. **Узнайте IP вашей машины:**
```bash
# Linux/Mac
ip addr show | grep "inet " | grep -v 127.0.0.1

# Или
hostname -I
```

2. **Обновите `.env.production`:**
```env
VITE_API_BASE_URL=http://192.168.1.XXX:8000
```
Замените `192.168.1.XXX` на реальный IP вашей машины!

3. **Запустите бэкенд на 0.0.0.0:**
```bash
./run_backend.sh
```

4. **Соберите и задеплойте фронтенд:**
```bash
cd frontend
npm run build
npm run deploy
```

#### Как это работает:

```
[GitHub Pages] ─────────────> [Ваш IP:8000]
   (браузер)      HTTP          (Django)
                запросы
                
Пример:
https://YurchenkoK.github.io/vasoactive_drug_speed_estimatior_frontend/
        ↓
делает запросы к
        ↓
http://192.168.1.240:8000/api/drugs/
```

**Важно:**
- GitHub Pages делает запросы НЕ с сервера GitHub, а из браузера пользователя
- Браузер подключается напрямую к вашему локальному IP
- Это работает только в пределах одной WiFi сети

### 3. Структура конфигурации

#### Frontend (drugsApi.ts)
```typescript
// Development: API_BASE_URL = '' (прокси через Vite)
// Production: API_BASE_URL = 'http://192.168.1.XXX:8000'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
```

#### Vite (vite.config.ts)
```typescript
server: {
  host: '0.0.0.0',  // Слушаем на всех интерфейсах
  proxy: {
    '/api': {
      target: 'http://0.0.0.0:8000',  // Проксируем на бэкенд
    }
  }
}
```

#### Django (settings.py)
```python
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

### 4. Подключение с телефона

1. Подключите телефон к той же WiFi сети, что и компьютер
2. Запустите бэкенд: `./run_backend.sh`
3. Узнайте IP (будет показан при запуске скрипта)
4. На телефоне откройте браузер:
   - Локальный фронт: `http://192.168.1.XXX:3000`
   - GH Pages: `https://YurchenkoK.github.io/vasoactive_drug_speed_estimatior_frontend/`

### 5. Troubleshooting

#### "Не могу подключиться по IP"
- Убедитесь, что firewall не блокирует порты 3000 и 8000
- Проверьте, что устройства в одной сети
- Попробуйте пинговать: `ping 192.168.1.XXX`

#### "CORS errors на GitHub Pages"
- Убедитесь, что в `settings.py`:
  ```python
  CORS_ALLOW_ALL_ORIGINS = True
  CORS_ALLOW_CREDENTIALS = True
  ```
- Проверьте, что бэкенд запущен на `0.0.0.0:8000`

#### "Connection refused"
- Бэкенд должен быть запущен на `0.0.0.0`, а не `127.0.0.1`
- Используйте скрипт `./run_backend.sh`

### 6. Файлы конфигурации

```
frontend/
├── .env.development      # Для npm run dev (прокси)
├── .env.production       # Для npm run build (прямой URL)
├── .env.example          # Пример конфигурации
└── vite.config.ts        # Настройки Vite

application/
└── settings.py           # CORS, ALLOWED_HOSTS

run_backend.sh            # Запуск Django на 0.0.0.0
run_frontend.sh           # Запуск React с IP
```

### 7. Архитектура

```
┌─────────────────────────────────────────┐
│   Development (локальная разработка)    │
├─────────────────────────────────────────┤
│                                         │
│  Browser ──> http://192.168.1.XXX:3000 │
│                    │                    │
│                    │ /api/* (proxy)     │
│                    ↓                    │
│             http://0.0.0.0:8000        │
│              (Django backend)           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│   Production (GitHub Pages)             │
├─────────────────────────────────────────┤
│                                         │
│  Browser ──> https://github.io/...     │
│       │              (static files)     │
│       │                                 │
│       │ fetch('http://192.168.1.XXX:8000/api/...')
│       │                                 │
│       └──────────────────────┐         │
│                              ↓         │
│                   http://192.168.1.XXX:8000
│                      (Django backend)   │
└─────────────────────────────────────────┘
```

## Команды

```bash
# Запуск всего стека для локальной разработки
./run_backend.sh    # В одном терминале
./run_frontend.sh   # В другом терминале

# Деплой на GitHub Pages
cd frontend
npm run build       # Собираем production build
npm run deploy      # Деплоим на GH Pages
```

## Безопасность

⚠️ **Внимание:** Конфигурация `CORS_ALLOW_ALL_ORIGINS = True` и `ALLOWED_HOSTS = ['*']` 
небезопасна для production! Это только для разработки и локального использования.

Для настоящего production сервера:
```python
CORS_ALLOWED_ORIGINS = [
    'https://yourchenkok.github.io',
]
ALLOWED_HOSTS = ['your-domain.com', 'your-ip']
```
