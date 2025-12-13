#!/bin/sh
# Скрипт для автоматической настройки IP в .env.production

cd "$(dirname "$0")/frontend" || exit

echo "=== Настройка IP для GitHub Pages ==="
echo ""

# Получаем IP адрес
IP=$(ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 | head -1)

if [ -z "$IP" ]; then
    echo "❌ Не удалось определить IP адрес автоматически"
    echo ""
    echo "Пожалуйста, введите IP адрес вручную:"
    read -r IP
fi

if [ -z "$IP" ]; then
    echo "❌ IP адрес не указан. Прерывание."
    exit 1
fi

echo "✅ Ваш IP адрес: $IP"
echo ""

# Обновляем .env.production
cat > .env.production << EOF
# Автоматически сгенерировано $(date)
# IP адрес Windows машины для GitHub Pages
VITE_API_BASE_URL=http://$IP:8005
EOF

echo "✅ Файл .env.production обновлен"
echo ""
echo "Содержимое:"
cat .env.production
echo ""
echo "──────────────────────────────────────"
echo "⚠️  ВАЖНО для Docker в Windows:"
echo "  1. Убедитесь, что порты пробросаны (docker ps)"
echo "  2. Настройте Windows Firewall (см. DOCKER_WINDOWS_SETUP.txt)"
echo "  3. Запустите бэкенд: ./run_backend.sh"
echo ""
echo "Теперь можно деплоить на GitHub Pages:"
echo "  cd frontend"
echo "  npm run build"
echo "  npm run deploy"
echo "──────────────────────────────────────"
