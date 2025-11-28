from rest_framework import permissions
from stocks.redis_client import redis_user_client


def get_redis_user(request):
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        user = request.user
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'role': user.role if hasattr(user, 'role') else 'USER'
        }
    
    session_id = request.COOKIES.get('redis_session_id')
    if session_id:
        return redis_user_client.get_session(session_id)
    
    return None


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            return True
        
        if hasattr(request, 'user') and request.user:
            return isinstance(request.user, dict)
        
        user = get_redis_user(request)
        return user is not None


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(request, 'user') and request.user and isinstance(request.user, dict):
            user = request.user
        else:
            user = get_redis_user(request)
        
        if not user:
            return False
        return user.get('is_staff', False) or user.get('is_superuser', False)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(request, 'user') and request.user and isinstance(request.user, dict):
            user = request.user
        else:
            user = get_redis_user(request)
        
        if not user:
            return False
        return user.get('is_superuser', False)
