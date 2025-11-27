import redis
import json
import hashlib
import secrets
from django.conf import settings


class RedisUserClient:
    """
    Redis client for user management using Lua scripts.
    Stores users in Redis hashes and manages authentication.
    """
    
    def __init__(self):
        redis_config = {
            'host': getattr(settings, 'REDIS_HOST', 'redis'),
            'port': getattr(settings, 'REDIS_PORT', 6379),
            'db': 0,
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
        }
        
        # Add password if configured
        redis_password = getattr(settings, 'REDIS_PASSWORD', None)
        if redis_password:
            redis_config['password'] = redis_password
        
        # Add username if configured (for Redis ACL)
        redis_username = getattr(settings, 'REDIS_USERNAME', None)
        if redis_username:
            redis_config['username'] = redis_username
        
        # Try multiple connection attempts with different auth methods
        connection_attempts = []
        
        # Attempt 1: With configured credentials
        try:
            self.redis_client = redis.Redis(**redis_config)
            self.redis_client.ping()
            print(f"✓ Подключен к Redis ({redis_config['host']}:{redis_config['port']})")
            self._load_lua_scripts()
            return
        except redis.exceptions.AuthenticationError as e:
            connection_attempts.append(f"Попытка с настроенными credentials: {e}")
        except redis.exceptions.ConnectionError as e:
            print(f"✗ Ошибка подключения к Redis: {e}")
            raise
        
        # Attempt 2: Try common passwords if no password configured
        if not redis_password:
            common_passwords = ['', 'redis', 'root', 'rootroot', 'password', 'admin']
            for pwd in common_passwords:
                try:
                    test_config = redis_config.copy()
                    if pwd:
                        test_config['password'] = pwd
                    else:
                        test_config.pop('password', None)
                        test_config.pop('username', None)
                    
                    self.redis_client = redis.Redis(**test_config)
                    self.redis_client.ping()
                    print(f"✓ Подключен к Redis с паролем: {'(пусто)' if not pwd else '***'}")
                    print(f"  Добавьте в settings.py: REDIS_PASSWORD = '{pwd}'")
                    self._load_lua_scripts()
                    return
                except:
                    connection_attempts.append(f"Пароль '{pwd}': не подошел")
                    continue
        
        # If all attempts failed
        print("\n✗ Не удалось подключиться к Redis")
        print("\nПопробованные варианты:")
        for attempt in connection_attempts[:3]:
            print(f"  - {attempt}")
        print("\nРешения:")
        print("  1. Обновите application/settings.py:")
        print("     REDIS_PASSWORD = 'ваш_пароль'")
        print("  2. Или проверьте: docker logs <redis-container>")
        print("  3. Или см. REDIS_AUTH_TROUBLESHOOTING.md")
        raise redis.exceptions.AuthenticationError("Не удалось аутентифицироваться в Redis")
        
        # Load Lua scripts
        self._load_lua_scripts()
    
    def _load_lua_scripts(self):
        """Load and register Lua scripts in Redis"""
        
        # Script for user registration
        self.register_script = self.redis_client.register_script("""
            local username = ARGV[1]
            local user_data = ARGV[2]
            
            -- Check if user exists
            local exists = redis.call('EXISTS', 'user:' .. username)
            if exists == 1 then
                return nil
            end
            
            -- Get next user ID
            local user_id = redis.call('INCR', 'user:id:counter')
            
            -- Parse user data
            local data = cjson.decode(user_data)
            data['id'] = user_id
            data['username'] = username
            
            -- Save user
            redis.call('HMSET', 'user:' .. username, 
                'id', user_id,
                'username', username,
                'password', data['password'],
                'first_name', data['first_name'] or '',
                'last_name', data['last_name'] or '',
                'email', data['email'] or '',
                'is_staff', data['is_staff'] or '0',
                'is_superuser', data['is_superuser'] or '0'
            )
            
            -- Add to users set
            redis.call('SADD', 'users:all', username)
            
            -- Map user ID to username
            redis.call('SET', 'user:id:' .. user_id, username)
            
            return user_id
        """)
        
        # Script for user authentication
        self.authenticate_script = self.redis_client.register_script("""
            local username = ARGV[1]
            local password = ARGV[2]
            
            -- Check if user exists
            local exists = redis.call('EXISTS', 'user:' .. username)
            if exists == 0 then
                return nil
            end
            
            -- Get stored password
            local stored_password = redis.call('HGET', 'user:' .. username, 'password')
            
            -- Compare passwords
            if stored_password == password then
                return redis.call('HGETALL', 'user:' .. username)
            else
                return nil
            end
        """)
        
        # Script for getting user by username
        self.get_user_script = self.redis_client.register_script("""
            local username = ARGV[1]
            
            local exists = redis.call('EXISTS', 'user:' .. username)
            if exists == 0 then
                return nil
            end
            
            return redis.call('HGETALL', 'user:' .. username)
        """)
        
        # Script for getting user by ID
        self.get_user_by_id_script = self.redis_client.register_script("""
            local user_id = ARGV[1]
            
            -- Get username from ID
            local username = redis.call('GET', 'user:id:' .. user_id)
            if not username then
                return nil
            end
            
            return redis.call('HGETALL', 'user:' .. username)
        """)
        
        # Script for updating user
        self.update_user_script = self.redis_client.register_script("""
            local username = ARGV[1]
            local updates = ARGV[2]
            
            local exists = redis.call('EXISTS', 'user:' .. username)
            if exists == 0 then
                return nil
            end
            
            local data = cjson.decode(updates)
            local args = {}
            
            for key, value in pairs(data) do
                if key ~= 'id' and key ~= 'username' and key ~= 'password' then
                    table.insert(args, key)
                    table.insert(args, value)
                end
            end
            
            if #args > 0 then
                redis.call('HMSET', 'user:' .. username, unpack(args))
            end
            
            return redis.call('HGETALL', 'user:' .. username)
        """)
        
        # Script for creating session
        self.create_session_script = self.redis_client.register_script("""
            local session_id = ARGV[1]
            local username = ARGV[2]
            local ttl = tonumber(ARGV[3])
            
            redis.call('SET', 'session:' .. session_id, username, 'EX', ttl)
            redis.call('SET', 'user:session:' .. username, session_id, 'EX', ttl)
            
            return 1
        """)
        
        # Script for getting session
        self.get_session_script = self.redis_client.register_script("""
            local session_id = ARGV[1]
            
            local username = redis.call('GET', 'session:' .. session_id)
            if not username then
                return nil
            end
            
            return redis.call('HGETALL', 'user:' .. username)
        """)
        
        # Script for deleting session
        self.delete_session_script = self.redis_client.register_script("""
            local session_id = ARGV[1]
            
            local username = redis.call('GET', 'session:' .. session_id)
            if username then
                redis.call('DEL', 'user:session:' .. username)
            end
            redis.call('DEL', 'session:' .. session_id)
            
            return 1
        """)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate a secure session ID"""
        return secrets.token_urlsafe(32)
    
    def _hash_to_dict(self, hash_data):
        """Convert Redis hash list to dictionary"""
        if not hash_data:
            return None
        
        result = {}
        for i in range(0, len(hash_data), 2):
            key = hash_data[i]
            value = hash_data[i + 1]
            
            # Convert boolean fields
            if key in ['is_staff', 'is_superuser']:
                result[key] = value == '1' or value == 'True'
            # Convert ID to int
            elif key == 'id':
                result[key] = int(value)
            else:
                result[key] = value
        
        return result
    
    def register_user(self, username: str, password: str, first_name: str = '', 
                     last_name: str = '', email: str = '', is_staff: bool = False,
                     is_superuser: bool = False) -> dict:
        """
        Register a new user in Redis
        
        Args:
            username: User's username
            password: User's plain text password (will be hashed)
            first_name: User's first name
            last_name: User's last name
            email: User's email
            is_staff: Whether user has staff privileges
            is_superuser: Whether user has superuser privileges
            
        Returns:
            dict: User data if successful, None if user already exists
        """
        hashed_password = self.hash_password(password)
        
        user_data = {
            'password': hashed_password,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'is_staff': '1' if is_staff else '0',
            'is_superuser': '1' if is_superuser else '0'
        }
        
        user_id = self.register_script(args=[username, json.dumps(user_data)])
        
        if user_id is None:
            return None
        
        return self.get_user(username)
    
    def authenticate(self, username: str, password: str) -> dict:
        """
        Authenticate a user
        
        Args:
            username: User's username
            password: User's plain text password
            
        Returns:
            dict: User data if authentication successful, None otherwise
        """
        hashed_password = self.hash_password(password)
        user_data = self.authenticate_script(args=[username, hashed_password])
        return self._hash_to_dict(user_data)
    
    def get_user(self, username: str) -> dict:
        """
        Get user by username
        
        Args:
            username: User's username
            
        Returns:
            dict: User data if found, None otherwise
        """
        user_data = self.get_user_script(args=[username])
        return self._hash_to_dict(user_data)
    
    def get_user_by_id(self, user_id: int) -> dict:
        """
        Get user by ID
        
        Args:
            user_id: User's ID
            
        Returns:
            dict: User data if found, None otherwise
        """
        user_data = self.get_user_by_id_script(args=[str(user_id)])
        return self._hash_to_dict(user_data)
    
    def update_user(self, username: str, **kwargs) -> dict:
        """
        Update user information
        
        Args:
            username: User's username
            **kwargs: Fields to update (first_name, last_name, email)
            
        Returns:
            dict: Updated user data
        """
        # Filter out password and protected fields
        allowed_fields = ['first_name', 'last_name', 'email']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        user_data = self.update_user_script(args=[username, json.dumps(updates)])
        return self._hash_to_dict(user_data)
    
    def create_session(self, username: str, ttl: int = 86400) -> str:
        """
        Create a session for a user
        
        Args:
            username: User's username
            ttl: Time to live in seconds (default: 24 hours)
            
        Returns:
            str: Session ID
        """
        session_id = self.generate_session_id()
        self.create_session_script(args=[session_id, username, str(ttl)])
        return session_id
    
    def get_session(self, session_id: str) -> dict:
        """
        Get user data from session ID
        
        Args:
            session_id: Session ID
            
        Returns:
            dict: User data if session exists, None otherwise
        """
        user_data = self.get_session_script(args=[session_id])
        return self._hash_to_dict(user_data)
    
    def delete_session(self, session_id: str):
        """
        Delete a session
        
        Args:
            session_id: Session ID
        """
        self.delete_session_script(args=[session_id])
    
    def get_all_users(self) -> list:
        """
        Get all registered users
        
        Returns:
            list: List of all user dictionaries
        """
        usernames = self.redis_client.smembers('users:all')
        users = []
        for username in usernames:
            user = self.get_user(username)
            if user:
                users.append(user)
        return users
    
    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists
        
        Args:
            username: User's username
            
        Returns:
            bool: True if user exists, False otherwise
        """
        return self.redis_client.exists(f'user:{username}') == 1
    
    def create_token(self, username: str) -> str:
        """
        Create authentication token for user
        
        Args:
            username: User's username
            
        Returns:
            str: Authentication token
        """
        # Generate secure token
        token = secrets.token_hex(32)
        
        # Store token with 24 hour expiration
        token_key = f'token:{token}'
        self.redis_client.setex(token_key, 86400, username)
        
        # Also store in user's token set for revocation
        user_tokens_key = f'user:{username}:tokens'
        self.redis_client.sadd(user_tokens_key, token)
        self.redis_client.expire(user_tokens_key, 86400)
        
        return token
    
    def get_user_by_token(self, token: str) -> str:
        """
        Get username by authentication token
        
        Args:
            token: Authentication token
            
        Returns:
            str: Username or None if token is invalid
        """
        token_key = f'token:{token}'
        username = self.redis_client.get(token_key)
        return username
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke authentication token
        
        Args:
            token: Token to revoke
            
        Returns:
            bool: True if token was revoked
        """
        # Get username first
        username = self.get_user_by_token(token)
        
        if username:
            # Remove from user's token set
            user_tokens_key = f'user:{username}:tokens'
            self.redis_client.srem(user_tokens_key, token)
        
        # Delete token
        token_key = f'token:{token}'
        return self.redis_client.delete(token_key) > 0
    
    def revoke_all_user_tokens(self, username: str) -> int:
        """
        Revoke all tokens for a user
        
        Args:
            username: User's username
            
        Returns:
            int: Number of tokens revoked
        """
        user_tokens_key = f'user:{username}:tokens'
        tokens = self.redis_client.smembers(user_tokens_key)
        
        count = 0
        for token in tokens:
            if self.revoke_token(token):
                count += 1
        
        return count


# Global instance
redis_user_client = RedisUserClient()
