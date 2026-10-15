from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.auth import (
    AccessTokenResponse,
    TokenPair,
    TokenRefreshRequest,
    UserLogin,
)
from app.schemas.user import UserCreate, UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
def register(data: UserCreate, session: Session = Depends(get_session)):
    try:
        user = auth_service.register(session, data)
    except auth_service.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado"
        )
    return user


@router.post("/login", response_model=TokenPair)
def login(data: UserLogin, session: Session = Depends(get_session)):
    try:
        return auth_service.login(session, data)
    except auth_service.InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrecto",
        )


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(data: TokenRefreshRequest, session: Session = Depends(get_session)):
    try:
        access_token = auth_service.refresh(session, data.refresh_token)
    except auth_service.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        )
    return AccessTokenResponse(access_token=access_token)
