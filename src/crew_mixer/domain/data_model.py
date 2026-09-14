from enum import Enum
from typing import Self
from uuid import UUID, uuid4
from datetime import date, datetime, time
from pydantic import BaseModel, Field, model_validator


class DayType(str, Enum):
    SCHEDULED = "scheduled"
    TOGETHER = "together"


class Day(BaseModel):
    date_index: int
    day_type: DayType
    together_text: str | None = None

    @model_validator(mode="after")
    def check_together_text(self) -> Self:
        if self.day_type == DayType.TOGETHER:
            if self.together_text is None:
                raise ValueError("No text provided for together day.")
        return self


class Area(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    color: str = Field(min_length=1)


class ShiftType(str, Enum):
    MORNING = "morning"
    MIDDAY = "midday"
    EVENING = "evening"
    NIGHT = "night"


class Shift(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    day_index: int
    start: time
    end: time
    shift_type: ShiftType
    area_id: UUID
    desired_volunteers: int = Field(gt=0)


class Marker(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    day_index: int
    start: time
    end: time
    note: str = Field(min_length=1)


class Gender(str, Enum):
    M = "male"
    W = "female"
    D = "divers"


class Volunteer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    gender: Gender


class Pair(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    volunteer_a_id: UUID
    volunteer_b_id: UUID


class Event(BaseModel):
    name: str = Field(min_length=1)
    starting_day: date
    days: list[Day] = []
    volunteers: list[Volunteer] = []
    pairs: list[Pair] = []
    areas: list[Area] = []
    shifts: list[Shift] = []
    markers: list[Marker] = []


class Assignment(BaseModel):
    shift_id: UUID
    volunteer_ids: list[UUID] = []


class Plan(BaseModel):
    assignments: list[Assignment] = []
    score: int
    created_at: datetime


class ProblemCode(str, Enum):
    NO_CODE = "nocode"


class Problem(BaseModel):
    code: ProblemCode
    data: str


class Project(BaseModel):
    schema_version: int = 1
    event: Event
    plan: Plan | None = None
