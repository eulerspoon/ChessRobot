import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import router
from config import TRANSPORT_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("robot_agent")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Агентный уровень запущен. Транспортный уровень ожидается по адресу {TRANSPORT_URL}")
    logger.info("Сервис работает без транспортного уровня, ошибки отправки будут логироваться")
    yield
    logger.info("Агентный уровень завершает работу")

app = FastAPI(
    title="Агентный уровень: Эмулятор роботизированной руки для игры в шахматы",
    description=(
        "Принимает шахматные ходы в нотации, проверяет их легальность с помощью библиотеки chess, "
        "эмулирует движение робота (2D координаты x, y) и отправляет телеметрию сегментами на транспортный уровень. "
        "Высота определяется состоянием захвата (empty/holding)."
    ),
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)