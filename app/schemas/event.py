from pydantic import BaseModel, Field, model_validator, ConfigDict
from datetime import datetime
from typing import Self
from app.models.enums import EventStatusEnum


class EventCreate(BaseModel):
    name: str
    description: str | None = None
    location: str
    start_date: datetime
    end_date: datetime
    capacity: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.end_date <= self.start_date:
            raise ValueError(
                "La fecha fin no puede ser menor o igual a la fecha de inicio del evento"
            )

        return self


class EventUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    location: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    capacity: int | None = Field(gt=0, default=None)


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organizer_id: int
    status: EventStatusEnum
    name: str
    description: str | None = None
    location: str
    start_date: datetime
    end_date: datetime
    capacity: int
    created_at: datetime
    updated_at: datetime


class EventListResponse(BaseModel):
    items: list[EventRead]
    total: int
    page: int
    page_size: int
