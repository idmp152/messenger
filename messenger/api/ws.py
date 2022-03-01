from pydantic import ValidationError

from fastapi import APIRouter, WebSocket
from typing import List, Callable, Coroutine

from messenger.api.user import get_user_by_token
from messenger.core.schemas.opcodes import BaseRequestContainer, SendRequest, Opcodes
from messenger.core.schemas.ws_responses import ErrorMessage, EventMessage, EventTypes
from messenger.core.models.message import Message
from messenger.core import async_sessionmaker

ws_router: APIRouter = APIRouter()

INVALID_REQUEST_FORMAT_ERROR: str = str(ErrorMessage(detail="Invalid request format.").dict())
INVALID_CREDENTIALS_ERROR: str = str(ErrorMessage(detail="Invalid credentials.").dict())


async def send_message(payload: SendRequest, ws_pool: List[WebSocket]) -> None:
    message_to_send = str(EventMessage(detail=payload.message, event_type=int(EventTypes.NEW_MESSAGE)).dict())
    for ws in ws_pool:
        await ws.send_text(message_to_send)
    user = await get_user_by_token(payload.token)
    async with async_sessionmaker() as sess:
        async with sess.begin():
            new_message = Message(author_id=user.id, content=payload.message)
            sess.add(new_message)


def response_factory(opcode: Opcodes) -> Callable[[SendRequest, List[WebSocket]], Coroutine]:
    if opcode == Opcodes.SEND_MESSAGE:
        return send_message


websocket_pool: List[WebSocket] = []


@ws_router.websocket("/api/ws")
async def websocket_connect(ws: WebSocket) -> None:
    await ws.accept()
    websocket_pool.append(ws)
    while True:
        data = await ws.receive_text()

        try:
            request_model = BaseRequestContainer.parse_raw(data).__root__
        except ValidationError:
            await ws.send_text(INVALID_REQUEST_FORMAT_ERROR)
            continue

        user = await get_user_by_token(request_model.token)
        if not user:
            await ws.send_text(INVALID_CREDENTIALS_ERROR)
            continue

        await response_factory(request_model.opcode)(request_model, websocket_pool)
