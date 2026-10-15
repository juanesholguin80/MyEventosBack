from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlmodel import Session

from app.core.security import decode_token
from app.db.session import get_session
from app.models.user import User
from app.repositories import user_repo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado"
        )

    if payload["type"] != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Tipo de token incorrecto"
        )

    user = user_repo.get_by_id(session, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inválido o inactivo",
        )

    return user


def require_roles(*roles):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta acción",
            )
        return current_user

    return dependency
