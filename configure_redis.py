#!/usr/bin/env python3
"""
Скрипт для настройки Redis аутентификации

Использование:
    python configure_redis.py --test          # Проверить подключение
    python configure_redis.py --setup         # Настроить Redis
    python configure_redis.py --create-admin  # Создать администратора
"""

import sys
import os
import argparse

# Добавляем путь к Django проекту
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')

import django
django.setup()

import redis
from django.conf import settings


def test_connection():
    """Проверка подключения к Redis"""
    print("Проверка подключения к Redis...")
    
    try:
        # Try with configured credentials
        redis_config = {
            'host': getattr(settings, 'REDIS_HOST', 'redis'),
            'port': getattr(settings, 'REDIS_PORT', 6379),
            'db': 0,
            'decode_responses': True,
            'socket_connect_timeout': 5
        }
        
        # Add password if configured
        redis_password = getattr(settings, 'REDIS_PASSWORD', None)
        if redis_password:
            redis_config['password'] = redis_password
        
        # Add username if configured
        redis_username = getattr(settings, 'REDIS_USERNAME', None)
        if redis_username:
            redis_config['username'] = redis_username
        
        client = redis.Redis(**redis_config)
        
        response = client.ping()
        print(f"✓ Подключение успешно (без аутентификации)")
        print(f"  Host: {settings.REDIS_HOST}")
        print(f"  Port: {settings.REDIS_PORT}")
        
        # Check server info
        info = client.info('server')
        print(f"  Redis version: {info.get('redis_version', 'unknown')}")
        
        return client
        
    except redis.exceptions.AuthenticationError:
        print("✗ Требуется аутентификация")
        print("\nОбновите settings.py:")
        print("  REDIS_PASSWORD = 'your_password'")
        print("  # REDIS_USERNAME = 'default'  # Если используется ACL")
        return None
        
    except redis.exceptions.ConnectionError as e:
        print(f"✗ Ошибка подключения: {e}")
        print("\nПроверьте, что Redis контейнер запущен:")
        print("  docker ps | grep redis")
        return None
        
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        return None


def setup_redis():
    """Настройка Redis для работы с приложением"""
    print("Настройка Redis...")
    
    client = test_connection()
    if not client:
        return False
    
    try:
        # Check if we can run Lua scripts
        test_script = client.register_script("return 'OK'")
        result = test_script()
        print("✓ Lua скрипты доступны")
        
        # Initialize user counter if not exists
        if not client.exists('user:id:counter'):
            client.set('user:id:counter', 0)
            print("✓ Инициализирован счетчик ID пользователей")
        else:
            counter = client.get('user:id:counter')
            print(f"✓ Счетчик ID пользователей: {counter}")
        
        # Check existing users
        users_count = client.scard('users:all')
        print(f"✓ Зарегистрировано пользователей: {users_count}")
        
        if users_count > 0:
            users = client.smembers('users:all')
            print(f"  Пользователи: {', '.join(users)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка настройки: {e}")
        return False


def create_admin():
    """Создать администратора"""
    print("Создание администратора...")
    
    try:
        from stocks.redis_client import redis_user_client
        
        # Check if admin exists
        if redis_user_client.user_exists('admin'):
            print("⚠ Пользователь 'admin' уже существует")
            
            # Show admin info
            admin = redis_user_client.get_user('admin')
            print(f"  ID: {admin['id']}")
            print(f"  Username: {admin['username']}")
            print(f"  Email: {admin.get('email', 'не указан')}")
            print(f"  is_staff: {admin.get('is_staff', False)}")
            print(f"  is_superuser: {admin.get('is_superuser', False)}")
            return
        
        # Create admin
        admin = redis_user_client.register_user(
            username='admin',
            password='admin123',
            first_name='Администратор',
            last_name='Системы',
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
        
        if admin:
            print("✓ Администратор создан успешно")
            print(f"  Username: admin")
            print(f"  Password: admin123")
            print(f"  ID: {admin['id']}")
            print("\n⚠ ВАЖНО: Смените пароль после первого входа!")
        else:
            print("✗ Не удалось создать администратора")
            
    except Exception as e:
        print(f"✗ Ошибка создания администратора: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description='Настройка Redis для аутентификации пользователей'
    )
    parser.add_argument(
        '--test', 
        action='store_true',
        help='Проверить подключение к Redis'
    )
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Настроить Redis для работы приложения'
    )
    parser.add_argument(
        '--create-admin',
        action='store_true',
        help='Создать пользователя-администратора'
    )
    
    args = parser.parse_args()
    
    # If no args, show help
    if not any([args.test, args.setup, args.create_admin]):
        parser.print_help()
        return
    
    if args.test:
        test_connection()
    
    if args.setup:
        setup_redis()
    
    if args.create_admin:
        create_admin()


if __name__ == '__main__':
    main()
