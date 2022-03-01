from pydantic import BaseModel, Field
from enum import Enum


class EventTypes(int, Enum):
    NEW_MESSAGE = 1


class Message(BaseModel):
    type: str
    detail: str


class ErrorMessage(Message):
    type = Field("error", const=True)


class SuccessMessage(Message):
    type = Field("success", const=True)


class EventMessage(Message):
    type = Field("event", const=True)
    event_type: int
