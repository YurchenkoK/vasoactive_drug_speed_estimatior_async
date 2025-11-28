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
        user_data = None
        
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Token '):
            token = auth_header.split(' ')[1]
            username = redis_user_client.get_user_by_token(token)
            if username:
                user_data = redis_user_client.get_user(username)
        
        if not user_data:
            session_id = request.COOKIES.get('redis_session_id')
            if session_id:
                user_data = redis_user_client.get_session(session_id)
        
        if user_data:
            # store Redis user data as a dict on request.user for compatibility
            request.user = user_data
        else:
            request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response
