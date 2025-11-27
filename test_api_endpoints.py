#!/usr/bin/env python3
"""
Быстрый тест API endpoints для Redis аутентификации
"""

import requests
import json

BASE_URL = "http://localhost:8000"
session = requests.Session()

def test_api():
    print("=" * 60)
    print("  ТЕСТИРОВАНИЕ API ENDPOINTS")
    print("=" * 60)
    
    # 1. Регистрация
    print("\n1. Регистрация нового пользователя...")
    response = session.post(
        f"{BASE_URL}/api/users/register/",
        json={
            "username": "apitest",
            "password": "test123456",
            "first_name": "API",
            "last_name": "Test",
            "email": "api@test.com"
        }
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # 2. Вход
    print("\n2. Вход в систему...")
    response = session.post(
        f"{BASE_URL}/api/users/login/",
        json={
            "username": "apitest",
            "password": "test123456"
        }
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   User ID: {data.get('id')}")
    print(f"   Username: {data.get('username')}")
    print(f"   is_staff: {data.get('is_staff')}")
    
    # 3. Получение текущего пользователя
    print("\n3. Получение текущего пользователя...")
    response = session.get(f"{BASE_URL}/api/users/me/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # 4. Обновление профиля
    print("\n4. Обновление профиля...")
    user_id = data.get('id')
    response = session.put(
        f"{BASE_URL}/api/users/profile/{user_id}/",
        json={
            "first_name": "Updated",
            "email": "updated@test.com"
        }
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # 5. Выход
    print("\n5. Выход из системы...")
    response = session.post(f"{BASE_URL}/api/users/logout/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # 6. Проверка что сессия удалена
    print("\n6. Проверка удаления сессии...")
    response = session.get(f"{BASE_URL}/api/users/me/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    print("\n" + "=" * 60)
    print("  ✓ Все API тесты завершены!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("✗ Не удалось подключиться к серверу")
        print("  Запустите сервер: python manage.py runserver 0.0.0.0:8000")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
