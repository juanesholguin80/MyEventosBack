from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.db.session import get_session
from app.api.v1.deps import get_current_user, get_current_user_optional, require_roles
from app.models.enums import EventStatusEnum, RoleEnum
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate, EventRead, EventListResponse
from app.services import event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    data: EventCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(RoleEnum.ORGANIZER, RoleEnum.ADMIN)),
):
    return event_service.create_event(session, data, current_user)


@router.get("", response_model=EventListResponse, status_code=status.HTTP_200_OK)
def get_events(
    name: str | None = None,
    status_filter: EventStatusEnum | None = Query(default=None, alias="status"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user_optional),
):
    return event_service.search_events(
        session, name, status_filter, date_from, date_to, page, page_size, current_user
    )


@router.get("/{event_id}", response_model=EventRead, status_code=status.HTTP_200_OK)
def get_event(
    event_id: int,
    session: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user_optional),
):
    try:
        return event_service.get_event(session, event_id, current_user)
    except event_service.EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )


@router.put("/{event_id}", response_model=EventRead, status_code=status.HTTP_200_OK)
def update_event(
    event_id: int,
    data: EventUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return event_service.update_event(session, event_id, data, current_user)
    except event_service.EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )
    except event_service.EventForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )
    except event_service.InvalidEventStateError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El evento no se puede editar en su estado actual",
        )
    except event_service.InvalidEventDataError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha fin debe ser posterior a la fecha de inicio",
        )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        event_service.delete_event(session, event_id, current_user)
    except event_service.EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )
    except event_service.EventForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )
    except event_service.InvalidEventStateError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El evento no se puede eliminar en su estado actual",
        )


def _handle_transition(
    session: Session,
    event_id: int,
    current_user: User,
    transition_func: Callable[[Session, int, User], object],
):
    try:
        return transition_func(session, event_id, current_user)
    except event_service.EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )
    except event_service.EventForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )
    except event_service.InvalidEventStateError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transición de estado inválida",
        )


@router.patch(
    "/{event_id}/publish", response_model=EventRead, status_code=status.HTTP_200_OK
)
def publish_event(
    event_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return _handle_transition(
        session, event_id, current_user, event_service.publish_event
    )


@router.patch(
    "/{event_id}/cancel", response_model=EventRead, status_code=status.HTTP_200_OK
)
def cancel_event(
    event_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return _handle_transition(
        session, event_id, current_user, event_service.cancel_event
    )


@router.patch(
    "/{event_id}/finish", response_model=EventRead, status_code=status.HTTP_200_OK
)
def finish_event(
    event_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return _handle_transition(
        session, event_id, current_user, event_service.finish_event
    )
