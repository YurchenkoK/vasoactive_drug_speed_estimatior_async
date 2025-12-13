# 🚀 Быстрая шпаргалка

## Локальная разработка

```bash
# Запуск бэкенда на 0.0.0.0:8000
./run_backend.sh

# Запуск фронтенда на 0.0.0.0:3000
./run_frontend.sh

# Или по отдельности:
python manage.py runserver 0.0.0.0:8000
cd frontend && npm run dev
```

## Деплой на GitHub Pages

```bash
# Полный автоматический деплой
./deploy_to_ghpages.sh

# Или по шагам:
./setup_ip_for_ghpages.sh  # Настройка IP
cd frontend
npm run build              # Сборка
npm run deploy             # Деплой
```

## Узнать свой IP

```bash
# Linux
ip addr show | grep "inet " | grep -v 127.0.0.1

# Или при запуске скриптов - IP будет показан
./run_backend.sh
```

## Доступ по сети

### С локальной машины:
- Фронт: `http://localhost:3000`
- Бэк: `http://localhost:8000`

### С другого устройства (телефон, планшет):
- Фронт: `http://192.168.1.XXX:3000`
- Бэк: `http://192.168.1.XXX:8000`
- GH Pages: `https://YurchenkoK.github.io/vasoactive_drug_speed_estimatior_frontend/`

## Структура конфигов

```
frontend/
├── .env.development   ← Для npm run dev (прокси)
├── .env.production    ← Для npm run build (прямой URL)
└── .env.example       ← Шаблон

VITE_API_BASE_URL=     # пусто = использовать прокси
VITE_API_BASE_URL=http://192.168.1.XXX:8000  # прямое подключение
```

## Troubleshooting

### "Connection refused"
```bash
# Убедитесь, что бэкенд запущен на 0.0.0.0
python manage.py runserver 0.0.0.0:8000
```

### "CORS errors"
```python
# В application/settings.py должно быть:
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

### "Не могу подключиться по IP"
```bash
# 1. Проверьте IP
ip addr show

# 2. Проверьте firewall (если есть)
# Linux: sudo ufw allow 3000
#        sudo ufw allow 8000

# 3. Убедитесь, что устройства в одной WiFi сети
```

## Архитектура

### Development (локально)
```
Browser → localhost:3000 → (Vite proxy) → localhost:8000
```

### Production (GH Pages)
```
Browser → github.io → (прямой HTTP) → 192.168.1.XXX:8000
         (статика)                    (локальный бэк)
```

## Важные файлы

| Файл | Назначение |
|------|-----------|
| `frontend/vite.config.ts` | Настройка прокси, host 0.0.0.0 |
| `frontend/src/drugsApi.ts` | API_BASE_URL из env переменных |
| `application/settings.py` | CORS, ALLOWED_HOSTS |
| `frontend/.env.production` | IP для GH Pages (генерируется) |

## Команды npm

```bash
cd frontend

npm run dev        # Разработка (localhost)
npm run dev:ip     # Разработка (0.0.0.0)
npm run build      # Сборка для production
npm run deploy     # Деплой на GitHub Pages
npm run preview    # Превью production сборки
```
