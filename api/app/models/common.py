import datetime

from pydantic import BaseModel, validator


class DateTimeModelMixin(BaseModel):
    created_at: datetime.datetime = None  # type: ignore
    updated_at: datetime.datetime = None  # type: ignore

    @validator("created_at", "updated_at", pre=True, always=True)
    def default_datetime(
        cls, value: datetime.datetime  # noqa: N805, WPS110
    ) -> datetime.datetime:
        return value or datetime.datetime.utcnow().replace(microsecond=0)


class IDModelMixin(BaseModel):
    id: int = 0