"""
Shared FastAPI dependencies: DB session access and JWT-authenticated
current-user resolution, used to protect routes.
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import TokenValidationError, get_subject_from_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.utils.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedError("Not authenticated.")

    try:
        subject = get_subject_from_token(token, expected_type="access")
    except TokenValidationError as exc:
        raise UnauthorizedError("Invalid or expired access token.") from exc

    user = db.query(User).filter(User.id == int(subject)).first()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")

    return user


def require_roles(*allowed_roles: UserRole):
    """Dependency factory for role-gated endpoints, e.g.
    Depends(require_roles(UserRole.ADMIN, UserRole.QA_MANAGER))"""

    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            from app.utils.exceptions import ForbiddenError

            raise ForbiddenError("You do not have permission to perform this action.")
        return user

    return _check
