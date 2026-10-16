from datetime import datetime

from app.schemas.event import EventCreate, EventUpdate, EventRead, EventListResponse
from app.repositories import event_repo
from sqlmodel import Session
from app.models.event import Event
from app.models.user import User
from app.models.enums import EventStatusEnum, RoleEnum


class EventNotFoundError(Exception):
    pass


class EventForbiddenError(Exception):
    pass


class InvalidEventStateError(Exception):
    pass


class InvalidEventDataError(Exception):
    pass


ALLOWED_TRANSITIONS = {
    EventStatusEnum.DRAFT: {EventStatusEnum.PUBLISHED},
    EventStatusEnum.PUBLISHED: {EventStatusEnum.CANCELLED, EventStatusEnum.FINISHED},
    EventStatusEnum.CANCELLED: set(),
    EventStatusEnum.FINISHED: set(),
}


def create_event(session: Session, data: EventCreate, current_user: User) -> Event:
    new_event = Event(
        name=data.name,
        description=data.description,
        location=data.location,
        start_date=data.start_date,
        end_date=data.end_date,
        capacity=data.capacity,
        status=EventStatusEnum.DRAFT,
        organizer_id=current_user.id,
    )

    event = event_repo.create(session, new_event)
    session.commit()

    return event


def update_event(
    session: Session, event_id: int, data: EventUpdate, current_user: User
) -> Event:
    event = event_repo.get_by_id(session, event_id)

    if not event:
        raise EventNotFoundError()

    if current_user.role != RoleEnum.ADMIN and event.organizer_id != current_user.id:
        raise EventForbiddenError()

    if event.status in (EventStatusEnum.CANCELLED, EventStatusEnum.FINISHED):
        raise InvalidEventStateError()

    update_fields = data.model_dump(exclude_unset=True)

    new_start = update_fields.get("start_date", event.start_date)
    new_end = update_fields.get("end_date", event.end_date)

    if new_start >= new_end:
        raise InvalidEventDataError()

    updated_event = event_repo.update(session, event, update_fields)

    session.commit()

    return updated_event


def delete_event(session: Session, event_id: int, current_user: User) -> None:
    event = event_repo.get_by_id(session, event_id)

    if not event:
        raise EventNotFoundError()

    if current_user.role != RoleEnum.ADMIN and event.organizer_id != current_user.id:
        raise EventForbiddenError()

    if event.status in (EventStatusEnum.CANCELLED, EventStatusEnum.FINISHED):
        raise InvalidEventStateError()

    event_repo.delete(session, event)
    session.commit()


def _transition_event(
    session: Session,
    event_id: int,
    current_user: User,
    target_status: EventStatusEnum,
) -> Event:
    event = event_repo.get_by_id(session, event_id)

    if not event:
        raise EventNotFoundError()

    if current_user.role != RoleEnum.ADMIN and event.organizer_id != current_user.id:
        raise EventForbiddenError()

    if target_status not in ALLOWED_TRANSITIONS[event.status]:
        raise InvalidEventStateError()

    event.status = target_status
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def publish_event(session: Session, event_id: int, current_user: User) -> Event:
    return _transition_event(session, event_id, current_user, EventStatusEnum.PUBLISHED)


def cancel_event(session: Session, event_id: int, current_user: User) -> Event:
    return _transition_event(session, event_id, current_user, EventStatusEnum.CANCELLED)


def finish_event(session: Session, event_id: int, current_user: User) -> Event:
    return _transition_event(session, event_id, current_user, EventStatusEnum.FINISHED)


def search_events(
    session: Session,
    name: str | None,
    status: EventStatusEnum | None,
    date_from: datetime | None,
    date_to: datetime | None,
    page: int,
    page_size: int,
    current_user: User | None,
) -> EventListResponse:
    offset = (page - 1) * page_size
    viewer_id = current_user.id if current_user else None
    is_admin = current_user.role == RoleEnum.ADMIN if current_user else False

    events = event_repo.list_with_filters(
        session,
        name,
        status,
        date_from,
        date_to,
        page_size,
        offset,
        viewer_id,
        is_admin,
    )
    total = event_repo.count_with_filters(
        session, name, status, date_from, date_to, viewer_id, is_admin
    )

    items = [EventRead.model_validate(event) for event in events]

    return EventListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


def get_event(session: Session, event_id: int, current_user: User | None) -> Event:
    event = event_repo.get_by_id(session, event_id)
    if not event:
        raise EventNotFoundError()

    is_owner_or_admin = current_user is not None and (
        current_user.role == RoleEnum.ADMIN or event.organizer_id == current_user.id
    )
    if event.status == EventStatusEnum.DRAFT and not is_owner_or_admin:
        raise EventNotFoundError()

    return event
