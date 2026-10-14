from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from sqlmodel import Session, select

from app.db.session import engine
from app.models import Event, Registration, Speaker, User
from app.models import Session as EventSession
from app.models.enums import EventStatusEnum, RegistrationStatusEnum, RoleEnum

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

ADMIN_EMAIL = "admin@miseventos.com"


def seed() -> None:
    with Session(engine) as session:
        existing_admin = session.exec(
            select(User).where(User.email == ADMIN_EMAIL)
        ).first()
        if existing_admin:
            print("El seed ya se corrió antes (el admin ya existe). No se insertó nada.")
            return

        admin = User(
            email=ADMIN_EMAIL,
            password_hash=pwd_context.hash("Admin123!"),
            full_name="Admin Principal",
            role=RoleEnum.ADMIN,
        )
        organizer = User(
            email="organizador@miseventos.com",
            password_hash=pwd_context.hash("Organizador123!"),
            full_name="Organizador Demo",
            role=RoleEnum.ORGANIZER,
        )
        assistant = User(
            email="asistente@miseventos.com",
            password_hash=pwd_context.hash("Asistente123!"),
            full_name="Asistente Demo",
            role=RoleEnum.ASSISTANT,
        )
        speaker = Speaker(
            full_name="Ponente Demo",
            bio="Experto invitado para la charla de apertura.",
            email="ponente@miseventos.com",
        )
        session.add_all([admin, organizer, assistant, speaker])
        session.flush()  # asigna los ids sin cerrar la transacción

        now = datetime.now(timezone.utc)
        start_date = now + timedelta(days=30)
        event = Event(
            organizer_id=organizer.id,
            name="Conferencia de Tecnología 2026",
            description="Evento demo generado por scripts/seed.py.",
            location="Centro de Convenciones, Bogotá",
            start_date=start_date,
            end_date=start_date + timedelta(hours=8),
            capacity=100,
            status=EventStatusEnum.PUBLISHED,
        )
        session.add(event)
        session.flush()

        event_session = EventSession(
            event_id=event.id,
            speaker_id=speaker.id,
            title="Charla de apertura",
            description="Sesión demo generada por scripts/seed.py.",
            start_time=start_date,
            end_time=start_date + timedelta(hours=1),
            capacity=50,
        )
        registration = Registration(
            user_id=assistant.id,
            event_id=event.id,
            status=RegistrationStatusEnum.CONFIRMED,
        )
        session.add_all([event_session, registration])
        session.commit()

        print("Seed completado: 3 usuarios, 1 ponente, 1 evento, 1 sesión, 1 inscripción.")


if __name__ == "__main__":
    seed()
