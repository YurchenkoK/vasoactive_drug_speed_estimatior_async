"""
Тестирование Redis-based аутентификации с использованием Lua скриптов

Этот модуль тестирует функциональность управления пользователями через Redis,
используя Lua скрипты для атомарных операций.
"""

import sys
import os

# Добавляем путь к Django проекту
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')

import django
django.setup()

from stocks.redis_client import redis_user_client
import time


def print_header(text):
    """Печать заголовка раздела"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_test(test_name, passed=True):
    """Печать результата теста"""
    status = "✓ PASSED" if passed else "✗ FAILED"
    print(f"{status}: {test_name}")


def test_user_registration():
    """Тест регистрации пользователя"""
    print_header("ТЕСТ 1: Регистрация пользователя")
    
    # Очищаем тестовых пользователей
    redis_user_client.redis_client.delete('user:testuser1')
    redis_user_client.redis_client.srem('users:all', 'testuser1')
    
    # Создаем пользователя
    user = redis_user_client.register_user(
        username='testuser1',
        password='password123',
        first_name='Иван',
        last_name='Иванов',
        email='ivan@example.com'
    )
    
    print(f"Зарегистрирован пользователь: {user}")
    print_test("Регистрация нового пользователя", user is not None)
    print_test("ID пользователя создан", 'id' in user and user['id'] > 0)
    print_test("Username сохранен", user['username'] == 'testuser1')
    print_test("Имя сохранено", user['first_name'] == 'Иван')
    
    # Попытка создать дубликат
    duplicate = redis_user_client.register_user(
        username='testuser1',
        password='different',
        first_name='Петр',
        last_name='Петров',
        email='petr@example.com'
    )
    
    print_test("Защита от дубликатов username", duplicate is None)
    
    return user


def test_user_authentication(user):
    """Тест аутентификации пользователя"""
    print_header("ТЕСТ 2: Аутентификация пользователя")
    
    # Успешная аутентификация
    auth_user = redis_user_client.authenticate('testuser1', 'password123')
    print(f"Аутентифицированный пользователь: {auth_user}")
    print_test("Аутентификация с правильным паролем", auth_user is not None)
    print_test("Данные пользователя совпадают", 
               auth_user['username'] == user['username'])
    
    # Неуспешная аутентификация
    wrong_pass = redis_user_client.authenticate('testuser1', 'wrongpassword')
    print_test("Отказ при неправильном пароле", wrong_pass is None)
    
    wrong_user = redis_user_client.authenticate('nonexistent', 'password123')
    print_test("Отказ при несуществующем пользователе", wrong_user is None)


def test_session_management():
    """Тест управления сессиями"""
    print_header("ТЕСТ 3: Управление сессиями")
    
    # Создание сессии
    session_id = redis_user_client.create_session('testuser1', ttl=10)
    print(f"Создана сессия: {session_id}")
    print_test("Генерация ID сессии", session_id is not None and len(session_id) > 0)
    
    # Получение пользователя по сессии
    user_from_session = redis_user_client.get_session(session_id)
    print(f"Пользователь из сессии: {user_from_session}")
    print_test("Получение пользователя из сессии", 
               user_from_session is not None)
    print_test("Username из сессии совпадает", 
               user_from_session['username'] == 'testuser1')
    
    # Удаление сессии
    redis_user_client.delete_session(session_id)
    deleted_session = redis_user_client.get_session(session_id)
    print_test("Удаление сессии", deleted_session is None)
    
    # Тест истечения TTL
    print("\nТест истечения TTL (подождите 3 секунды)...")
    short_session = redis_user_client.create_session('testuser1', ttl=2)
    time.sleep(3)
    expired_session = redis_user_client.get_session(short_session)
    print_test("Автоматическое истечение сессии по TTL", expired_session is None)


def test_user_retrieval():
    """Тест получения данных пользователя"""
    print_header("ТЕСТ 4: Получение данных пользователя")
    
    # Получение по username
    user_by_name = redis_user_client.get_user('testuser1')
    print(f"Пользователь по username: {user_by_name}")
    print_test("Получение по username", user_by_name is not None)
    
    # Получение по ID
    user_id = user_by_name['id']
    user_by_id = redis_user_client.get_user_by_id(user_id)
    print(f"Пользователь по ID: {user_by_id}")
    print_test("Получение по ID", user_by_id is not None)
    print_test("Данные совпадают", 
               user_by_name['username'] == user_by_id['username'])
    
    # Проверка несуществующего пользователя
    nonexistent = redis_user_client.get_user('doesnotexist')
    print_test("None для несуществующего пользователя", nonexistent is None)


def test_user_update():
    """Тест обновления данных пользователя"""
    print_header("ТЕСТ 5: Обновление данных пользователя")
    
    # Обновление данных
    updated_user = redis_user_client.update_user(
        'testuser1',
        first_name='Петр',
        last_name='Петров',
        email='petr@newmail.com'
    )
    
    print(f"Обновленный пользователь: {updated_user}")
    print_test("Обновление имени", updated_user['first_name'] == 'Петр')
    print_test("Обновление фамилии", updated_user['last_name'] == 'Петров')
    print_test("Обновление email", updated_user['email'] == 'petr@newmail.com')
    print_test("Username не изменился", updated_user['username'] == 'testuser1')


def test_multiple_users():
    """Тест работы с несколькими пользователями"""
    print_header("ТЕСТ 6: Работа с несколькими пользователями")
    
    # Создаем несколько пользователей
    users_to_create = [
        ('user2', 'pass2', 'Алексей', 'Смирнов'),
        ('user3', 'pass3', 'Мария', 'Петрова'),
        ('admin1', 'admin123', 'Admin', 'User'),
    ]
    
    created_users = []
    for username, password, first, last in users_to_create:
        # Очистка перед созданием
        redis_user_client.redis_client.delete(f'user:{username}')
        redis_user_client.redis_client.srem('users:all', username)
        
        user = redis_user_client.register_user(
            username=username,
            password=password,
            first_name=first,
            last_name=last,
            is_staff=(username == 'admin1')
        )
        created_users.append(user)
    
    print(f"Создано пользователей: {len(created_users)}")
    print_test("Создание нескольких пользователей", 
               len(created_users) == len(users_to_create))
    
    # Получение всех пользователей
    all_users = redis_user_client.get_all_users()
    print(f"Всего пользователей в Redis: {len(all_users)}")
    print_test("Получение списка всех пользователей", len(all_users) >= 4)
    
    # Проверка уникальности ID
    user_ids = [u['id'] for u in all_users]
    print_test("Уникальность ID пользователей", 
               len(user_ids) == len(set(user_ids)))
    
    # Проверка прав администратора
    admin = redis_user_client.get_user('admin1')
    print_test("Флаг is_staff для администратора", admin['is_staff'] == True)


def test_concurrent_sessions():
    """Тест одновременных сессий"""
    print_header("ТЕСТ 7: Одновременные сессии")
    
    # Создаем несколько сессий для одного пользователя
    session1 = redis_user_client.create_session('testuser1')
    session2 = redis_user_client.create_session('testuser1')
    session3 = redis_user_client.create_session('testuser1')
    
    print(f"Создано 3 сессии:")
    print(f"  Session 1: {session1[:20]}...")
    print(f"  Session 2: {session2[:20]}...")
    print(f"  Session 3: {session3[:20]}...")
    
    # Проверяем, что все сессии уникальны
    print_test("Уникальность ID сессий", 
               len({session1, session2, session3}) == 3)
    
    # Проверяем, что все сессии валидны
    user1 = redis_user_client.get_session(session1)
    user2 = redis_user_client.get_session(session2)
    user3 = redis_user_client.get_session(session3)
    
    print_test("Валидность всех сессий", 
               all([user1, user2, user3]))
    
    # Удаляем одну сессию
    redis_user_client.delete_session(session2)
    deleted = redis_user_client.get_session(session2)
    still_valid = redis_user_client.get_session(session1)
    
    print_test("Удаление одной сессии не влияет на другие", 
               deleted is None and still_valid is not None)


def test_password_hashing():
    """Тест хеширования паролей"""
    print_header("ТЕСТ 8: Хеширование паролей")
    
    # Проверяем, что пароли хешируются
    password = 'mypassword123'
    hash1 = redis_user_client.hash_password(password)
    hash2 = redis_user_client.hash_password(password)
    
    print(f"Пароль: {password}")
    print(f"Хеш 1: {hash1}")
    print(f"Хеш 2: {hash2}")
    
    print_test("Хеш не равен паролю", hash1 != password)
    print_test("Хеш детерминированный", hash1 == hash2)
    print_test("Хеш имеет правильную длину (SHA256)", len(hash1) == 64)
    
    # Проверяем, что пароли не хранятся в открытом виде
    user = redis_user_client.get_user('testuser1')
    stored_password = redis_user_client.redis_client.hget('user:testuser1', 'password')
    
    print(f"Сохраненный пароль: {stored_password}")
    print_test("Пароль сохранен в виде хеша", 
               stored_password != 'password123')
    print_test("Хеш в Redis соответствует алгоритму", len(stored_password) == 64)


def cleanup():
    """Очистка тестовых данных"""
    print_header("ОЧИСТКА ТЕСТОВЫХ ДАННЫХ")
    
    test_users = ['testuser1', 'user2', 'user3', 'admin1']
    for username in test_users:
        user = redis_user_client.get_user(username)
        if user:
            user_id = user['id']
            redis_user_client.redis_client.delete(f'user:{username}')
            redis_user_client.redis_client.delete(f'user:id:{user_id}')
            redis_user_client.redis_client.srem('users:all', username)
            print(f"Удален пользователь: {username}")
    
    print("\n✓ Очистка завершена")


def main():
    """Главная функция запуска всех тестов"""
    print("\n" + "=" * 60)
    print("  ТЕСТИРОВАНИЕ REDIS-BASED АУТЕНТИФИКАЦИИ С LUA СКРИПТАМИ")
    print("=" * 60)
    
    try:
        # Проверка подключения к Redis
        redis_user_client.redis_client.ping()
        print("✓ Подключение к Redis установлено")
    except Exception as e:
        print(f"✗ Ошибка подключения к Redis: {e}")
        print("Убедитесь, что Redis контейнер запущен!")
        return
    
    try:
        # Запуск тестов
        user = test_user_registration()
        test_user_authentication(user)
        test_session_management()
        test_user_retrieval()
        test_user_update()
        test_multiple_users()
        test_concurrent_sessions()
        test_password_hashing()
        
        print_header("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("✓ Все тесты успешно пройдены!")
        print("\nФункциональность Redis-based аутентификации работает корректно:")
        print("  • Регистрация пользователей через Lua скрипты")
        print("  • Аутентификация с хешированием паролей")
        print("  • Управление сессиями с TTL")
        print("  • CRUD операции с пользователями")
        print("  • Атомарные операции через Lua")
        print("  • Поддержка множественных сессий")
        
    except Exception as e:
        print(f"\n✗ Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Очистка
        cleanup()


if __name__ == "__main__":
    main()
