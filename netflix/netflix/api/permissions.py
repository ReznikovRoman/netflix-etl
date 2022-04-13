from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """Является ли текущий пользователь суперпользователем."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_superuser)
