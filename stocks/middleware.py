from stocks.redis_client import redis_user_client


class SimpleUser:
    def __init__(self, username, role='user', is_authenticated=True):
        self.username = username
        self.role = role
        self.is_authenticated = is_authenticated
        self.is_anonymous = not is_authenticated
        
    def __str__(self):
        return self.username
    
    def __repr__(self):
        return f"<SimpleUser: {self.username}>"


class AnonymousUser:
    username = 'anonymous'
    role = 'anonymous'
    is_authenticated = False
    is_anonymous = True
    
    def __str__(self):
        return 'AnonymousUser'
    
    def __repr__(self):
        return '<AnonymousUser>'


class RedisUserMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        token = None
        
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            token = request.COOKIES.get('auth_token')
        
        if token:
            user_data = redis_user_client.get_user_by_token(token)
            
            if user_data:
                request.user = SimpleUser(
                    username=user_data['username'],
                    role=user_data.get('role', 'user'),
                    is_authenticated=True
                )
            else:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response
