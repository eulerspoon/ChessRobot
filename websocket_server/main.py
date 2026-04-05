"""
Прикладной уровень — WebSocket-сервер на FastAPI.

"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import httpx
import json
import logging

from models import SendMessage, ReceiveMessage

HOST = "0.0.0.0"
PORT = 8001

TRANSPORT_LEVEL_HOST = "192.168.1.100"
TRANSPORT_LEVEL_PORT = 8080
TRANSPORT_LEVEL_URL = f"http://{TRANSPORT_LEVEL_HOST}:{TRANSPORT_LEVEL_PORT}/send"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app-level")

app = FastAPI(
    title="Прикладной уровень — Шахматная роботизированная рука",
    description=(
        "Система обмена сообщениями и телеметрией в реальном времени.\n\n"
        "**Телеметрия:** роботизированная рука играет в шахматы. "
        "Задаётся последовательность ходов в нотации. "
        "Транслируется положение захвата, координаты фигуры на доске и статус захвата.\n\n"
        "**Прототип дизайна:** lichess.org"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        if username in self.active:
            self.active[username].append(websocket)
        else:
            self.active[username] = [websocket]
        logger.info(f"[open] Connected: {username}")

    def disconnect(self, websocket: WebSocket, username: str):
        if username in self.active:
            self.active[username] = [ws for ws in self.active[username] if ws != websocket]
            if not self.active[username]:
                del self.active[username]
        logger.info(f"[close] Disconnected: {username}")

    async def broadcast(self, message: dict, exclude_username: Optional[str] = None):
        msg_str = json.dumps(message, ensure_ascii=False)
        for username, connections in self.active.items():
            if username != exclude_username:
                for ws in connections:
                    try:
                        await ws.send_text(msg_str)
                    except Exception as e:
                        logger.error(f"Error sending to {username}: {e}")

    async def send_to_user(self, username: str, message: dict):
        msg_str = json.dumps(message, ensure_ascii=False)
        if username in self.active:
            for ws in self.active[username]:
                try:
                    await ws.send_text(msg_str)
                except Exception as e:
                    logger.error(f"Error sending to {username}: {e}")


manager = ConnectionManager()


async def send_to_transport_level(message: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(TRANSPORT_LEVEL_URL, json=message)
            if response.status_code == 200:
                logger.info("Transport level responded OK")
                return response.json()
            else:
                logger.error(f"Transport level error: {response.status_code}")
                message["error"] = f"Transport level error: {response.status_code}"
                return message
    except Exception as e:
        logger.error(f"Cannot reach transport level: {e}")
        message["error"] = f"Transport level unavailable: {str(e)}"
        return message


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, username: str):
    """
    WebSocket-соединение для оператора.
    Подключение: ws://host:8001/ws?username=Оператор1
    """
    await manager.connect(websocket, username)

    try:
        while True:
            raw = await websocket.receive_text()
            logger.info(f"[message] From {username}: {raw}")

            message = json.loads(raw)
            message["username"] = message.get("username", username)
            message["send_time"] = message.get("send_time", datetime.now().isoformat())

            response_msg = await send_to_transport_level(message)

            if response_msg.get("error"):
                await manager.send_to_user(username, response_msg)

    except WebSocketDisconnect:
        manager.disconnect(websocket, username)
    except Exception as e:
        logger.error(f"WebSocket error for {username}: {e}")
        manager.disconnect(websocket, username)


@app.post(
    "/api/send",
    response_model=SendMessage,
    tags=["Методы прикладного уровня"],
    summary="Отправить ход роботу",
    description=(
        "Получает от клиента JSON с данными о шахматном ходе "
        "и отправляет их на транспортный уровень через HTTP-запрос."
    ),
    responses={
        200: {
            "description": "Ход успешно отправлен на транспортный уровень",
            "content": {
                "application/json": {
                    "example": {
                        "username": "Оператор1",
                        "send_time": "2025-04-05T14:30:00",
                        "data": "Переместить пешку",
                        "move_notation": "e2e4",
                        "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
                    }
                }
            }
        }
    },
)
async def send_message(message: SendMessage):
    msg_dict = message.model_dump(mode="json")
    await send_to_transport_level(msg_dict)
    return message


@app.post(
    "/api/receive",
    response_model=ReceiveMessage,
    tags=["Методы прикладного уровня"],
    summary="Принять телеметрию от транспортного уровня",
    description=(
        "Ожидает POST-запросы от транспортного уровня. "
        "Тело запроса — JSON с телеметрией робота: отправитель, время, "
        "признак ошибки, положение захвата, статус. "
        "Полученные данные рассылаются всем подключённым WebSocket-клиентам."
    ),
    responses={
        200: {
            "description": "Телеметрия доставлена всем подключённым операторам",
            "content": {
                "application/json": {
                    "example": {
                        "username": "RobotArm",
                        "timestamp": "2025-04-05T14:30:05",
                        "data": "Ход e2e4 выполнен",
                        "error": None,
                        "move_notation": "e2e4",
                        "gripper_position": {"x": 150.0, "y": 200.0},
                        "gripper_status": "holding",
                        "move_success": True,
                        "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
                    }
                }
            }
        }
    },
)
async def receive_message(message: ReceiveMessage):
    msg_dict = message.model_dump(mode="json")
    await manager.broadcast(msg_dict)
    return message


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
