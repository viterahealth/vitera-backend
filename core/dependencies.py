from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.security import decode_access_token
from database.models.user_models import UsersRole
from auth.auth_schema import Identity

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Identity:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    payload = decode_access_token(credentials.credentials)
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return Identity(user_id=payload["user_id"], email=payload["email"], role=UsersRole(payload["role"]))


def require_roles(*allowed_roles: UsersRole):
    """Usage: Depends(require_roles(UsersRole.ADMIN, UsersRole.DOCTOR))"""

    def dependency(identity: Identity = Depends(get_current_identity)) -> Identity:
        if identity.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {identity.role.value} is not permitted to do this",
            )
        return identity

    return dependency