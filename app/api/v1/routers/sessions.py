from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.db.session import get_session
from app.api.v1.deps import get_current_user, get_current_user_optional, require_roles
from app.models.enums import RoleEnum
from app.models.user import User
from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionRead,
    SessionListResponse,
)
from app.services import session_service, event_service

router = APIRouter(prefix="/events/{event_id}/sessions", tags=["sessions"])


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def create_session(
    event_id: int,
    data: SessionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(RoleEnum.ORGANIZER, RoleEnum.ADMIN)),
):
    try:
        return session_service.create_session(session, event_id, data, current_user)
    except event_service.EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )
    except event_service.EventForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )
    except session_service.SpeakerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ponente no encontrado"
        )
    except session_service.InvalidSessionDataError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El horario o la capacidad de la sesión no son válidos para este evento",
        )
    except session_service.SessionOverlapError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El ponente ya tiene otra sesión programada en ese horario",
        )


@router.get("", response_model=SessionListResponse, status_code=status.HTTP_200_OK)
def get_sessions(
    event_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user_optional),
):
    try:
        return session_service.list_sessions_by_event(
            session, event_id, page, page_size, current_user
        )
    except event_service.EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )


@router.get(
    "/{session_id}", response_model=SessionRead, status_code=status.HTTP_200_OK
)
def get_session_detail(
    event_id: int,
    session_id: int,
    session: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user_optional),
):
    try:
        return session_service.get_session(session, event_id, session_id, current_user)
    except event_service.EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )
    except session_service.SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada"
        )


@router.put(
    "/{session_id}", response_model=SessionRead, status_code=status.HTTP_200_OK
)
def update_session(
    event_id: int,
    session_id: int,
    data: SessionUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return session_service.update_session(
            session, event_id, session_id, data, current_user
        )
    except event_service.EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )
    except event_service.EventForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )
    except session_service.SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada"
        )
    except session_service.SpeakerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ponente no encontrado"
        )
    except session_service.InvalidSessionDataError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El horario o la capacidad de la sesión no son válidos para este evento",
        )
    except session_service.SessionOverlapError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El ponente ya tiene otra sesión programada en ese horario",
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    event_id: int,
    session_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        session_service.delete_session(session, event_id, session_id, current_user)
    except event_service.EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )
    except event_service.EventForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )
    except session_service.SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada"
        )
