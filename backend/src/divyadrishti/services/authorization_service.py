"""Authorization service."""

from divyadrishti.models import User
from divyadrishti.security.authorization import Role, has_permission


class AuthorizationService:
    """Check user permissions and roles."""

    @staticmethod
    def is_admin(user: User) -> bool:
        return user.is_superuser or (user.role is not None and user.role.name in {Role.ADMIN, Role.SUPER_ADMIN})

    @staticmethod
    def is_researcher_or_above(user: User) -> bool:
        if user.is_superuser:
            return True
        if not user.role:
            return False
        return user.role.name in {Role.RESEARCHER, Role.ADMIN, Role.SUPER_ADMIN}

    @staticmethod
    def can_access_resource(user: User, resource_user_id: int) -> bool:
        if user.is_superuser:
            return True
        return user.id == resource_user_id

    @staticmethod
    def check_permission(user: User, permission: str) -> bool:
        return has_permission(user, permission)
