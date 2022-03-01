import uvicorn
import asyncio

from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import Iterable

from messenger.core.models import Base
from messenger.core import db_engine
from messenger.api.user import user_router
from messenger.api.ws import ws_router
from messenger.config import SSL_KEYFILE_PATH, SSL_CERTFILE_PATH, HOST, PORT

app: FastAPI = FastAPI()
routers: Iterable[APIRouter] = (user_router, ws_router)


async def start_db_engine_async(engine: AsyncEngine, schema) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(schema.metadata.create_all)


if __name__ == "__main__":
    for router in routers:
        app.include_router(router)
    asyncio.run(start_db_engine_async(db_engine, Base))
    uvicorn.run(app,
                host=HOST,
                port=PORT,
                ssl_keyfile=SSL_KEYFILE_PATH,
                ssl_certfile=SSL_CERTFILE_PATH
                )
