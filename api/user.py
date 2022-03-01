import jwt

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.sql import select
from hashlib import sha256
from typing import Union

from messenger.core import async_sessionmaker
from messenger.core.models import user as model_user
from messenger.core.schemas import user as schema_user
from messenger.api import validators
from messenger.config import JWT_SECRET

user_router: APIRouter = APIRouter(prefix="/api/user")
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/api/user/login")

INVALID_CREDENTIALS_ERROR: HTTPException = HTTPException(detail="Invalid credentials.",
                                                         status_code=status.HTTP_401_UNAUTHORIZED)
USER_ID_DOES_NOT_EXIST_ERROR: HTTPException = HTTPException(detail=f"User with the given id does not exist.",
                                                            status_code=status.HTTP_400_BAD_REQUEST)
INVALID_USERNAME_FORMAT_ERROR: HTTPException = HTTPException(detail="Invalid username format.",
                                                             status_code=status.HTTP_400_BAD_REQUEST)
INVALID_PASSWORD_FORMAT_ERROR: HTTPException = HTTPException(detail="Invalid password format.",
                                                             status_code=status.HTTP_400_BAD_REQUEST)
INVALID_EMAIL_FORMAT_ERROR: HTTPException = HTTPException(detail="Invalid email format.",
                                                          status_code=status.HTTP_400_BAD_REQUEST)
USERNAME_ALREADY_EXISTS_ERROR: HTTPException = HTTPException(detail="User with the given username already exists.",
                                                             status_code=status.HTTP_400_BAD_REQUEST)
USERNAME_DOES_NOT_EXIST_ERROR: HTTPException = HTTPException(detail="User with the given username does not exist.",
                                                             status_code=status.HTTP_401_UNAUTHORIZED)
WRONG_PASSWORD_ERROR: HTTPException = HTTPException(detail="Wrong password for the given username.",
                                                    status_code=status.HTTP_401_UNAUTHORIZED)


async def get_user_by_token(token: str) -> Union[schema_user.User, None]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.DecodeError:
        return None
    async with async_sessionmaker() as sess:
        async with sess.begin():
            user = await sess.get(model_user.User, payload["id"])
            user_model = schema_user.User.from_orm(user) if user else None

    return user_model


@user_router.get("/me", response_model=schema_user.ResponseUser)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> schema_user.ResponseUser:
    user = await get_user_by_token(token)
    if not user:
        raise INVALID_CREDENTIALS_ERROR
    user_model = schema_user.ResponseUser.from_orm(user)
    return user_model


@user_router.get("/{user_id}", response_model=schema_user.ResponseUser)
async def get_user_from_db(user_id: int, token: str = Depends(oauth2_scheme)) -> schema_user.ResponseUser:
    if not await get_user_by_token(token):
        raise INVALID_CREDENTIALS_ERROR
    async with async_sessionmaker() as sess:
        async with sess.begin():
            user = await sess.get(model_user.User, user_id)
            if not user:
                raise USER_ID_DOES_NOT_EXIST_ERROR
            user_model = schema_user.ResponseUser.from_orm(user)

    return user_model


@user_router.post("/register")
async def register_user(user: schema_user.InputUser) -> None:
    if not validators.validate_username(user.username):
        raise INVALID_USERNAME_FORMAT_ERROR
    elif not validators.validate_password(user.password):
        raise INVALID_PASSWORD_FORMAT_ERROR
    elif not validators.validate_email(user.email):
        raise INVALID_EMAIL_FORMAT_ERROR
    async with async_sessionmaker() as sess:
        async with sess.begin():
            statement = select(model_user.User).filter_by(username=user.username)
            if (await sess.execute(statement)).scalar():
                raise USERNAME_ALREADY_EXISTS_ERROR
            db_user = model_user.User(username=user.username,
                                      pwd_hash=sha256(user.password.encode("utf-8")).hexdigest(),
                                      email=user.email)
            sess.add(db_user)


@user_router.post("/login")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    async with async_sessionmaker() as sess:
        async with sess.begin():
            statement = select(model_user.User).filter_by(username=form_data.username)
            user = (await sess.execute(statement)).scalar()
            if not user:
                raise USERNAME_DOES_NOT_EXIST_ERROR
            if not user.verify_password(form_data.password):
                raise WRONG_PASSWORD_ERROR
            user_model = schema_user.User.from_orm(user)
    return {"token": jwt.encode(user_model.dict(), JWT_SECRET), "type": "Bearer"}
