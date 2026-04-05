from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class GripperStatus(str, Enum):
    """Статус захвата роботизированной руки """
    OPENING = "opening"
    CLOSING = "closing"
    HOLDING = "holding"
    EMPTY = "empty"
    ERROR = "error"


class MessageType(str, Enum):
    """Тип сообщения: текст или файл"""
    TEXT = "text"
    FILE = "file"



class GripperPosition(BaseModel):
    """Координаты захвата роботизированной руки (x, y, z)"""
    x: float = Field(..., description="Координата X захвата (мм)", examples=[150.0])
    y: float = Field(..., description="Координата Y захвата (мм)", examples=[200.0])
    z: float = Field(..., description="Координата Z захвата (мм)", examples=[50.0])



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
    type: MessageType = Field(
        default=MessageType.TEXT,
        description="Тип сообщения: text или file"
    )
    data: Optional[str] = Field(
        None,
        description="Текст сообщения или base64-файл",
        examples=["Переместить пешку"]
    )
    move_notation: Optional[str] = Field(
        None,
        description="Ход в шахматной нотации",
        examples=["e2e4"]
    )



class ReceiveMessage(BaseModel):

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
    type: MessageType = Field(
        default=MessageType.TEXT,
        description="Тип сообщения"
    )
    data: Optional[str] = Field(
        None,
        description="Текст сообщения или base64-файл",
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
        description="Координаты захвата (x, y, z) или углы поворотов"
    )
    target_piece_coordinates: Optional[str] = Field(
        None,
        description="Координаты фигуры на доске (например, 'e4')",
        examples=["e4"]
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
