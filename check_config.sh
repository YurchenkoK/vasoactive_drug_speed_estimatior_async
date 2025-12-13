#!/bin/sh
# Скрипт для проверки конфигурации

echo "╔══════════════════════════════════════════════════╗"
echo "║  Проверка конфигурации IP доступа                ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Проверка IP
echo "📍 1. Проверка IP адреса..."
IP=$(ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 | head -1)
if [ -n "$IP" ]; then
    echo "   ✅ IP адрес: $IP"
else
    echo "   ❌ Не удалось определить IP адрес"
fi
echo ""

# Проверка портов
echo "🔌 2. Проверка доступности портов..."
if command -v netstat > /dev/null 2>&1; then
    if netstat -tuln 2>/dev/null | grep -q ":8005"; then
        echo "   ✅ Порт 8005 (Django) занят"
    else
        echo "   ⚠️  Порт 8005 свободен (запустите бэкенд)"
    fi
    
    if netstat -tuln 2>/dev/null | grep -q ":3005"; then
        echo "   ✅ Порт 3005 (Vite) занят"
    else
        echo "   ⚠️  Порт 3005 свободен (запустите фронтенд)"
    fi
else
    echo "   ℹ️  netstat не найден, пропуск проверки портов"
fi
echo ""

# Проверка файлов конфигурации
echo "📝 3. Проверка файлов конфигурации..."

if [ -f "frontend/.env.development" ]; then
    echo "   ✅ frontend/.env.development существует"
else
    echo "   ❌ frontend/.env.development не найден"
fi

if [ -f "frontend/.env.production" ]; then
    echo "   ✅ frontend/.env.production существует"
    echo "      Содержимое:"
    cat "frontend/.env.production" | sed 's/^/      /'
else
    echo "   ⚠️  frontend/.env.production не найден (запустите ./setup_ip_for_ghpages.sh)"
fi
echo ""

# Проверка settings.py
echo "🔧 4. Проверка Django settings..."
if grep -q "CORS_ALLOW_ALL_ORIGINS = True" application/settings.py 2>/dev/null; then
    echo "   ✅ CORS_ALLOW_ALL_ORIGINS = True"
else
    echo "   ❌ CORS_ALLOW_ALL_ORIGINS не настроен"
fi

if grep -q "ALLOWED_HOSTS = \['127.0.0.1', 'localhost', '\*'\]" application/settings.py 2>/dev/null; then
    echo "   ✅ ALLOWED_HOSTS настроен для всех хостов"
else
    echo "   ⚠️  Проверьте ALLOWED_HOSTS в settings.py"
fi
echo ""

# Итоговая информация
echo "╔══════════════════════════════════════════════════╗"
echo "║  Итого                                           ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "Для локальной разработки:"
echo "  Фронт: http://localhost:3005 или http://$IP:3005"
echo "  Бэк:   http://localhost:8005 или http://$IP:8005"
echo ""
echo "Для GitHub Pages:"
echo "  1. Запустите: ./setup_ip_for_ghpages.sh"
echo "  2. Запустите: ./run_backend.sh"
echo "  3. Деплойте: cd frontend && npm run deploy"
echo ""
echo "Команды:"
echo "  ./run_backend.sh         - Запуск бэкенда"
echo "  ./run_frontend.sh        - Запуск фронтенда"
echo "  ./deploy_to_ghpages.sh   - Полный деплой на GH Pages"
