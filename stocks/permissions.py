from rest_framework import permissions


class IsManager(permissions.BasePermission):
    """
    Пользовательское разрешение: пользователь является менеджером или администратором
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.is_staff or request.user.is_superuser))


class IsAdmin(permissions.BasePermission):
    """
    Пользовательское разрешение: пользователь является администратором
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.is_superuser)
