from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class GripperStatus(str, Enum):
    """Статус захвата роботизированной руки"""
    OPENING = "opening"
    CLOSING = "closing"
    HOLDING = "holding"
    EMPTY = "empty"
    ERROR = "error"


class GripperPosition(BaseModel):
    """Координаты захвата роботизированной руки (x, y)"""
    x: float = Field(..., description="Координата X захвата (мм)", examples=[150.0])
    y: float = Field(..., description="Координата Y захвата (мм)", examples=[200.0])


class SendMessage(BaseModel):
    """
    Сообщение от оператора — шахматный ход для робота.
    """
    username: str = Field(
        ..., min_length=1,
        description="Имя оператора",
        examples=["Оператор1"]
    )
    send_time: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Время отправки (ISO 8601)",
        examples=["2025-04-05T14:30:00"]
    )
    data: Optional[str] = Field(
        None,
        description="Текст сообщения",
        examples=["Переместить пешку"]
    )
    move_notation: Optional[str] = Field(
        None,
        description="Ход в шахматной нотации",
        examples=["e2e4"]
    )
    fen: Optional[str] = Field(
        None,
        description="Актуальная позиция на доске в формате FEN",
        examples=["rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"]
    )


class ReceiveMessage(BaseModel):
    """
    Телеметрия от робота.
    """
    username: str = Field(
        ...,
        description="Имя отправителя (робот)",
        examples=["RobotArm"]
    )
    timestamp: str = Field(
        ...,
        description="Время отправки (ISO 8601)",
        examples=["2025-04-05T14:30:05"]
    )
    data: Optional[str] = Field(
        None,
        description="Текст сообщения",
        examples=["Ход e2e4 выполнен"]
    )
    error: Optional[str] = Field(
        None,
        description="Признак ошибки. Если не пустое — в чате отображается иконка ошибки",
        examples=[None]
    )
    move_notation: Optional[str] = Field(
        None,
        description="Ход в шахматной нотации",
        examples=["e2e4"]
    )
    gripper_position: Optional[GripperPosition] = Field(
        None,
        description="Координаты захвата (x, y)"
    )
    gripper_status: Optional[GripperStatus] = Field(
        None,
        description="Статус захвата: opening / closing / holding / empty / error"
    )
    move_success: Optional[bool] = Field(
        None,
        description="Флаг успешности выполнения хода в целом",
        examples=[True]
    )
    fen: Optional[str] = Field(
        None,
        description="Позиция на доске в формате FEN",
        examples=["rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"]
    )
