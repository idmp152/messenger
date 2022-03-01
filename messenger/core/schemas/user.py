from pydantic import BaseModel


class InputUser(BaseModel):
    username: str
    password: str
    email: str


class ResponseUser(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    username: str
    pwd_hash: str
    email: str

    class Config:
        orm_mode = True
