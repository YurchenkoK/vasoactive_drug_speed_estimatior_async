#!/bin/sh

# Скрипт для тестирования ЛР8 - Асинхронный сервис

echo "╔════════════════════════════════════════════════════════╗"
echo "║         Тестирование ЛР8 - Асинхронный сервис         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Проверка работы сервисов
echo "→ Проверка Django сервиса (порт 8000)..."
DJANGO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/drugs/)
if [ "$DJANGO_STATUS" = "200" ]; then
    echo "✓ Django работает"
else
    echo "✗ Django не отвечает (код: $DJANGO_STATUS)"
    exit 1
fi

echo "→ Проверка Go сервиса (порт 8081)..."
GO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health)
if [ "$GO_STATUS" = "200" ]; then
    echo "✓ Go сервис работает"
else
    echo "✗ Go сервис не отвечает (код: $GO_STATUS)"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Все сервисы работают корректно!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Следующие шаги:"
echo "1. Откройте Insomnia"
echo "2. Импортируйте Insomnia_LAB8_Requests.json"
echo "3. Выполните запросы по порядку"
echo "4. Следите за изменением async_results_count"
echo ""
echo "Документация: TESTING_LAB8.md"
echo ""
