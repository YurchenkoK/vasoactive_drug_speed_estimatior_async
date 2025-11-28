from rest_framework import permissions
from stocks.redis_client import redis_user_client


def get_redis_user(request):
    # If middleware or DRF authentication placed a dict-like user (from Redis), return it
    if hasattr(request, 'user') and request.user:
        if isinstance(request.user, dict):
            return request.user
        # Normal Django-like user object
        if getattr(request.user, 'is_authenticated', False):
            user = request.user
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'role': user.role if hasattr(user, 'role') else 'USER'
            }
    
    session_id = request.COOKIES.get('session_id')
    if session_id:
        return redis_user_client.get_session(session_id)
    
    return None


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        # dict user (from Redis auth) -> authenticated
        if isinstance(user, dict):
            return True
        # Django user object
        if getattr(user, 'is_authenticated', False):
            return True

        # Fallback to Redis session lookup
        redis_user = get_redis_user(request)
        return redis_user is not None


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = None
        if hasattr(request, 'user') and isinstance(request.user, dict):
            user = request.user
        else:
            user = get_redis_user(request)
        
        if not user:
            return False
        return user.get('is_staff', False) or user.get('is_superuser', False)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = None
        if hasattr(request, 'user') and isinstance(request.user, dict):
            user = request.user
        else:
            user = get_redis_user(request)
        
        if not user:
            return False
        return user.get('is_superuser', False)
