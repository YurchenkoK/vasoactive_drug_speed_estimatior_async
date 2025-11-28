from rest_framework import authentication, exceptions
from stocks.redis_client import redis_user_client
import secrets


class RedisTokenAuthentication(authentication.BaseAuthentication):
    keyword = 'Token'
    
    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        
        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)
        
        return self.authenticate_credentials(token)
    
    def authenticate_credentials(self, key):
        username = redis_user_client.get_user_by_token(key)
        
        if not username:
            raise exceptions.AuthenticationFailed('Invalid token.')
        
        user = redis_user_client.get_user(username)
        
        if not user:
            raise exceptions.AuthenticationFailed('User not found.')
        
        return (user, key)
    
    def authenticate_header(self, request):
        return self.keyword


class RedisCookieAuthentication(authentication.BaseAuthentication):
    
    def authenticate(self, request):
        session_id = request.COOKIES.get('redis_session_id')
        
        if not session_id:
            return None
        
        user = redis_user_client.get_session(session_id)
        
        if not user:
            return None
        
        return (user, session_id)
    
    def authenticate_header(self, request):
        return 'Cookie'
