#!/bin/sh
# Полный процесс деплоя на GitHub Pages

echo "╔═══════════════════════════════════════════════════╗"
echo "║  Деплой на GitHub Pages с локальным бэкендом     ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Шаг 1: Настройка IP
echo "📍 Шаг 1: Настройка IP адреса..."
./setup_ip_for_ghpages.sh

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при настройке IP. Прерывание."
    exit 1
fi

echo ""
read -p "Продолжить деплой? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Деплой отменен."
    exit 0
fi

# Шаг 2: Сборка
echo ""
echo "🔨 Шаг 2: Сборка приложения..."
cd frontend || exit

npm run build

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при сборке. Прерывание."
    exit 1
fi

# Шаг 3: Деплой
echo ""
echo "🚀 Шаг 3: Деплой на GitHub Pages..."
npm run deploy

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при деплое. Прерывание."
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║  ✅ Деплой завершен успешно!                     ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "📝 Не забудьте:"
echo "  1. Запустить бэкенд: ./run_backend.sh"
echo "  2. Убедиться, что устройство в той же WiFi сети"
echo ""
echo "🌐 Ваше приложение:"
echo "  https://YurchenkoK.github.io/vasoactive_drug_speed_estimatior_frontend/"
