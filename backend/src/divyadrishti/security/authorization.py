"""Authorization and role-based access control."""

from enum import Enum
from functools import wraps
from typing import Callable

from fastapi import Depends, HTTPException, status

from divyadrishti.models import User
from divyadrishti.security.auth import get_current_user


class Role(str, Enum):
    USER = "user"
    RESEARCHER = "researcher"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Ordered by privilege level
ROLE_HIERARCHY = [Role.USER, Role.RESEARCHER, Role.ADMIN, Role.SUPER_ADMIN]


def require_role(*allowed_roles: str) -> Callable:
    """Dependency factory that restricts access to users with the given roles."""

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user
        if current_user.role and current_user.role.name in allowed_roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )

    return checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin or super admin role."""
    return require_role(Role.ADMIN, Role.SUPER_ADMIN)(current_user)


def has_permission(user: User, permission: Permission | str) -> bool:
    """Check if a user has a permission."""
    if user.is_superuser:
        return True
    if not user.role or not user.role.permissions:
        return False
    permission_value = permission.value if isinstance(permission, Permission) else permission
    return permission_value in user.role.permissions.split(",")


def require_permission(permission: Permission) -> Callable:
    """Dependency factory that checks a specific permission."""

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if has_permission(current_user, permission):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing permission: {permission.value}",
        )

    return checker
