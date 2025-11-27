from rest_framework import permissions
from stocks.redis_client import redis_user_client


def get_redis_user(request):
    """
    Получить текущего пользователя из Redis.
    Сначала проверяет request.user (установленный DRF authentication),
    затем fallback на cookie.
    """
    # Check if DRF authentication already set the user
    if hasattr(request, 'user') and request.user and isinstance(request.user, dict):
        return request.user
    
    # Fallback to cookie-based session
    session_id = request.COOKIES.get('redis_session_id')
    if not session_id:
        return None
    return redis_user_client.get_session(session_id)


class IsAuthenticated(permissions.BasePermission):
    """
    Проверка аутентификации через Redis (Token или Cookie)
    """
    def has_permission(self, request, view):
        # DRF authentication already checked
        if hasattr(request, 'user') and request.user:
            return isinstance(request.user, dict)
        
        # Fallback check
        user = get_redis_user(request)
        return user is not None


class IsManager(permissions.BasePermission):
    """
    Пользовательское разрешение: пользователь является менеджером или администратором
    """
    def has_permission(self, request, view):
        if hasattr(request, 'user') and request.user and isinstance(request.user, dict):
            user = request.user
        else:
            user = get_redis_user(request)
        
        if not user:
            return False
        return user.get('is_staff', False) or user.get('is_superuser', False)


class IsAdmin(permissions.BasePermission):
    """
    Пользовательское разрешение: пользователь является администратором
    """
    def has_permission(self, request, view):
        if hasattr(request, 'user') and request.user and isinstance(request.user, dict):
            user = request.user
        else:
            user = get_redis_user(request)
        
        if not user:
            return False
        return user.get('is_superuser', False)
