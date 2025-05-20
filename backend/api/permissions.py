from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Пользовательское разрешение для проверки доступа.

    Разрешает:
    - Анонимным пользователям только чтение
    - Авторизованным пользователям создавать объекты
    - Изменять и удалять объекты только их авторам
    """

    def has_object_permission(self, request, view, obj):
        """Проверяет права доступа к конкретному объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
