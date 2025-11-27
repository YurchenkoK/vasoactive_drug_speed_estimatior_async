"""
Custom DRF authentication backends for Redis-based users
"""
from rest_framework import authentication, exceptions
from stocks.redis_client import redis_user_client
import secrets


class RedisTokenAuthentication(authentication.BaseAuthentication):
    """
    Token-based authentication using Redis.
    Clients should authenticate by passing the token in the "Authorization" HTTP header,
    prepended with the string "Token ". For example:
    
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
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
        """
        Authenticate token and return user from Redis
        """
        # Get username from token
        username = redis_user_client.get_user_by_token(key)
        
        if not username:
            raise exceptions.AuthenticationFailed('Invalid token.')
        
        # Get user data
        user = redis_user_client.get_user(username)
        
        if not user:
            raise exceptions.AuthenticationFailed('User not found.')
        
        return (user, key)
    
    def authenticate_header(self, request):
        return self.keyword


class RedisCookieAuthentication(authentication.BaseAuthentication):
    """
    Cookie-based authentication using Redis sessions.
    Used for browser-based clients that work with cookies.
    """
    
    def authenticate(self, request):
        session_id = request.COOKIES.get('redis_session_id')
        
        if not session_id:
            return None
        
        # Get user from session
        user = redis_user_client.get_session(session_id)
        
        if not user:
            return None
        
        return (user, session_id)
    
    def authenticate_header(self, request):
        return 'Cookie'
