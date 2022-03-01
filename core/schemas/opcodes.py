from pydantic import BaseModel, Field
from typing import Union
from enum import Enum


class Opcodes(int, Enum):
    SEND_MESSAGE = 1


class BaseRequest(BaseModel):
    opcode: int
    token: str


class SendRequest(BaseRequest):
    opcode = Field(Opcodes.SEND_MESSAGE, const=True)
    message: str


class BaseRequestContainer(BaseModel):
    __root__: Union[SendRequest]
