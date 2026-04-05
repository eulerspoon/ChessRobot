from pydantic import BaseModel, Field, field_validator
from typing import Optional

class GripperPosition(BaseModel):
    x: float = Field(..., description="Координата X (0..7)", ge=0, le=7)
    y: float = Field(..., description="Координата Y (0..7)", ge=0, le=7)

class MoveCommand(BaseModel):
    move_notation: str = Field(
        ...,
        description="Ход в шахматной нотации (например, 'e2e4')",
        min_length=4,
        max_length=5,
        examples=["e2e4", "g1f3"]
    )

    @field_validator("move_notation")
    @classmethod
    def validate_notation(cls, v: str) -> str:
        if len(v) not in (4, 5):
            raise ValueError("Нотация должна содержать 4 или 5 символов")

        if not (v[0] in "abcdefgh" and v[1] in "12345678" and v[2] in "abcdefgh" and v[3] in "12345678"):
            raise ValueError("Неверный формат нотации, используйте, например, 'e2e4'")
        return v

class TelemetryData(BaseModel):
    username: str = Field(default="RobotArm", description="Имя отправителя (робот)")
    timestamp: str = Field(..., description="Время отправки в формате ISO 8601")
    type: str = Field(default="telemetry", description="Тип сообщения")
    data: Optional[str] = Field(None, description="Текстовое описание события")
    error: Optional[str] = Field(None, description="Сообщение об ошибке")
    move_notation: Optional[str] = Field(None, description="Выполняемый ход")
    gripper_position: Optional[GripperPosition] = Field(None, description="Координаты захвата (x, y)")
    target_piece_coordinates: Optional[str] = Field(None, description="Целевая клетка (например, 'e4')")
    gripper_status: Optional[str] = Field(None, description="Статус захвата: empty / holding / error")
    move_success: Optional[bool] = Field(None, description="Флаг успешности хода")
    fen: Optional[str] = Field(None, description="Позиция FEN (опционально)")

class Segment(BaseModel):
    message_id: str = Field(..., description="Уникальный ID сообщения (timestamp)")
    total_segments: int = Field(..., description="Общее число сегментов", ge=1)
    segment_number: int = Field(..., description="Номер сегмента (1-indexed)", ge=1)
    payload: str = Field(..., description="Часть сериализованного JSON телеметрии")