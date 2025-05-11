from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.BasePermission):
    """Чтение или доступно только Администратору/Автору."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or obj.author == request.user
        )
