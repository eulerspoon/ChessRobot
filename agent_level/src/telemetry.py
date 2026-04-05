import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
from config import TRANSPORT_URL, SEGMENT_SIZE
from models import TelemetryData, Segment, GripperPosition

logger = logging.getLogger("robot_agent")

async def send_segments(telemetry: TelemetryData):
    """Разбивает телеметрию на сегменты и отправляет на транспортный уровень."""
    telemetry_json = telemetry.model_dump_json(exclude_none=True)
    payload_bytes = telemetry_json.encode('utf-8')
    total_len = len(payload_bytes)
    total_segments = (total_len + SEGMENT_SIZE - 1) // SEGMENT_SIZE
    message_id = telemetry.timestamp

    async with httpx.AsyncClient(timeout=5.0) as client:
        for seg_num in range(1, total_segments + 1):
            start = (seg_num - 1) * SEGMENT_SIZE
            end = min(start + SEGMENT_SIZE, total_len)
            segment_payload = payload_bytes[start:end].decode('utf-8')
            segment = Segment(
                message_id=message_id,
                total_segments=total_segments,
                segment_number=seg_num,
                payload=segment_payload
            )
            try:
                response = await client.post(
                    f"{TRANSPORT_URL}/transfer",
                    json=segment.model_dump(),
                    timeout=2.0
                )
                response.raise_for_status()
                logger.debug(f"Сегмент {seg_num}/{total_segments} отправлен")
            except Exception as e:
                logger.error(f"Не удалось отправить сегмент {seg_num}: {e}")

async def send_telemetry(
    move_notation: str,
    target_square: Optional[str],
    gripper_pos: GripperPosition,
    gripper_status: str,
    data_msg: str = "",
    error_msg: Optional[str] = None,
    move_success: Optional[bool] = None
):
    """Формирует и отправляет один пакет телеметрии."""
    now = datetime.utcnow().isoformat() + "Z"
    telemetry = TelemetryData(
        timestamp=now,
        move_notation=move_notation,
        gripper_position=gripper_pos,
        gripper_status=gripper_status,
        target_piece_coordinates=target_square,
        data=data_msg or None,
        error=error_msg,
        move_success=move_success
    )
    await send_segments(telemetry)