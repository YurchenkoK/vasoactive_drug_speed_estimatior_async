#!/bin/sh
# Скрипт для запуска фронтенда в режиме разработки
# Сервер будет доступен по IP адресу

cd "$(dirname "$0")/frontend" || exit

echo "╔════════════════════════════════════════════════╗"
echo "║  Запуск React на 0.0.0.0:3005                 ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "⚠️  ВЫ В DOCKER КОНТЕЙНЕРЕ!"
echo ""

# Получаем IP адрес контейнера (для информации)
CONTAINER_IP=$(ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 | head -1)
if [ -n "$CONTAINER_IP" ]; then
    echo "📦 IP контейнера: $CONTAINER_IP (это НЕ ваш внешний IP)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  ВАЖНО для доступа с другого устройства:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Узнайте IP вашей Windows машины:"
echo "   - Откройте PowerShell/CMD на Windows"
echo "   - Выполните: ipconfig"
echo "   - Найдите IPv4 адрес (192.168.X.X)"
echo ""
echo "2. Убедитесь, что Docker пробросил порты:"
echo "   - Добавьте в docker-compose.yml или docker run:"
echo "   - ports: \"3005:3005\""
echo ""
echo "3. Подключайтесь по адресу:"
echo "   - http://WINDOWS_IP:3005"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Запуск сервера..."
npm run dev
