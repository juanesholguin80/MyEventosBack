from pydantic import BaseModel, ConfigDict, model_validator, Field
from datetime import datetime
from typing import Self


class SessionCreate(BaseModel):
    speaker_id: int
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    capacity: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.end_time <= self.start_time:
            raise ValueError(
                "La fecha fin no puede ser menor o igual a la fecha de inicio de la sesión"
            )

        return self


class SessionUpdate(BaseModel):
    speaker_id: int | None = None
    title: str | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    capacity: int | None = Field(gt=0, default=None)


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    speaker_id: int
    event_id: int
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    capacity: int


class SessionListResponse(BaseModel):
    items: list[SessionRead]
    total: int
    page: int
    page_size: int
