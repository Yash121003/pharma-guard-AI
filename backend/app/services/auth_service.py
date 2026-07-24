"""
Authentication business logic: user registration, credential verification,
and token issuance. Kept separate from the API layer so it's independently
testable and reusable (e.g. from a CLI seed script).
"""
import logging

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_subject_from_token,
    hash_password,
    verify_password,
    TokenValidationError,
)
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLogin, UserRegister
from app.utils.exceptions import ConflictError, UnauthorizedError

logger = logging.getLogger(__name__)


def register_user(db: Session, payload: UserRegister) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise ConflictError(f"A user with email '{payload.email}' already exists.")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Registered new user id=%s email=%s", user.id, user.email)
    return user


def authenticate_user(db: Session, payload: UserLogin) -> User:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password.")
    if not user.is_active:
        raise UnauthorizedError("This account has been deactivated.")
    return user


def issue_tokens(user: User) -> TokenResponse:
    subject = str(user.id)
    return TokenResponse(
        access_token=create_access_token(subject, extra_claims={"role": user.role.value}),
        refresh_token=create_refresh_token(subject),
    )


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
    try:
        subject = get_subject_from_token(refresh_token, expected_type="refresh")
    except TokenValidationError as exc:
        raise UnauthorizedError("Invalid or expired refresh token.") from exc

    user = db.query(User).filter(User.id == int(subject)).first()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")

    return issue_tokens(user)
