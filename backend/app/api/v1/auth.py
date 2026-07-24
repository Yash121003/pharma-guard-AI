"""
Authentication endpoints: register, login, logout, token refresh, and the
current-user profile check.

Note on "logout": since we use stateless JWTs (no server-side session
store), logout is handled by the client discarding its tokens. The
/auth/logout endpoint still exists so the frontend has a single, auditable
call site -- it records an audit log entry and returns 204.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    RefreshRequest,
    TokenResponse,
    UserLogin,
    UserPublic,
    UserRegister,
)
from app.services import auth_service
from app.services.audit_service import log_action

router = APIRouter()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    user = auth_service.register_user(db, payload)
    log_action(db, user_id=user.id, action="register", entity_type="user", entity_id=user.id)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = auth_service.authenticate_user(db, payload)
    tokens = auth_service.issue_tokens(user)
    log_action(db, user_id=user.id, action="login", entity_type="user", entity_id=user.id)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.refresh_access_token(db, payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    log_action(db, user_id=current_user.id, action="logout", entity_type="user", entity_id=current_user.id)
    return None


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
