from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.v1.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.registration import MyRegistrationsResponse, RegistrationRead
from app.services import registration_service
from app.services.event_service import EventNotFoundError

router = APIRouter(tags=["registrations"])


@router.post(
    "/events/{event_id}/register",
    response_model=RegistrationRead,
    status_code=status.HTTP_201_CREATED,
)
def register_to_event(
    event_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return registration_service.register_to_event(session, event_id, current_user)
    except EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )
    except registration_service.EventNotPublishedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El evento no está publicado",
        )
    except registration_service.AlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya estás registrado en este evento",
        )
    except registration_service.EventFullError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El evento no tiene cupo disponible",
        )


@router.delete("/events/{event_id}/register", status_code=status.HTTP_204_NO_CONTENT)
def cancel_registration(
    event_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        registration_service.cancel_registration(session, event_id, current_user)
    except registration_service.RegistrationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No estabas registrado en este evento",
        )


@router.get(
    "/me/registrations",
    response_model=MyRegistrationsResponse,
    status_code=status.HTTP_200_OK,
)
def get_my_registrations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return registration_service.list_my_registrations(
        session, current_user, page, page_size
    )
