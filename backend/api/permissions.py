from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Пользовательское разрешение для проверки доступа.
    
    Разрешает:
    - Анонимным пользователям только чтение
    - Авторизованным пользователям создавать объекты
    - Изменять и удалять объекты только их авторам или админам
    """
    
    def has_permission(self, request, view):
        """Проверяет общие права доступа на уровне запроса."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Проверяет права доступа к конкретному объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )
