from rest_framework import permissions
from drugs_estimation.redis_client import redis_user_client


def get_redis_user(request):
    if hasattr(request, 'user') and request.user:
        if isinstance(request.user, dict):
            return request.user
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
        user_data = redis_user_client.get_session(session_id)
        if user_data:
            return user_data
    
    admin_user = redis_user_client.get_user('admin')
    if admin_user:
        return admin_user
    
    return None


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
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
