import random
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from models import MoveCommand
from robot_state import robot_state
from chess_logic import is_legal_move, apply_move, get_board_fen
from telemetry import send_telemetry
from config import MOVE_DELAY, ERROR_PROBABILITY

router = APIRouter()

def chess_square_to_xy(square: str):
    """e2 -> (4, 1)  (0-indexed)"""
    col = ord(square[0]) - ord('a')
    row = int(square[1]) - 1
    return float(col), float(row)

async def emulate_move(move_notation: str):
    """Фоновая задача эмуляции движения с проверкой правил."""
    from_sq = move_notation[:2]
    to_sq = move_notation[2:4]
    from_x, from_y = chess_square_to_xy(from_sq)
    to_x, to_y = chess_square_to_xy(to_sq)

    async with robot_state.lock:
        if robot_state.gripper_status != "empty":
            await send_telemetry(
                move_notation, None,
                robot_state.current_position, "error",
                error_msg="Робот уже держит фигуру", move_success=False
            )
            return
        robot_state.current_move_notation = move_notation

    try:
        # перемещение к начальной клетке
        robot_state.current_position.x = from_x
        robot_state.current_position.y = from_y
        await send_telemetry(move_notation, from_sq, robot_state.current_position, "empty", "Перемещение к фигуре")
        await asyncio.sleep(MOVE_DELAY)

        # захват фигуры (симуляция)
        capture_ok = random.random() > ERROR_PROBABILITY
        if capture_ok:
            robot_state.gripper_status = "holding"
            await send_telemetry(move_notation, from_sq, robot_state.current_position, "holding", "Фигура захвачена")
        else:
            robot_state.gripper_status = "empty"
            await send_telemetry(
                move_notation, from_sq, robot_state.current_position, "error",
                error_msg="Ошибка захвата фигуры", move_success=False
            )
            return
        await asyncio.sleep(MOVE_DELAY)

        # перемещение к целевой клетке
        robot_state.current_position.x = to_x
        robot_state.current_position.y = to_y
        await send_telemetry(move_notation, to_sq, robot_state.current_position, "holding", "Перемещение к целевой клетке")
        await asyncio.sleep(MOVE_DELAY)

        # отпускание фигуры
        robot_state.gripper_status = "empty"
        await send_telemetry(move_notation, to_sq, robot_state.current_position, "empty", "Фигура отпущена")

        # смотрим, возможен ли ход
        if not apply_move(move_notation):
            # На всякий случай, если ход стал нелегальным (не должно случиться)
            await send_telemetry(
                move_notation, to_sq, robot_state.current_position, "error",
                error_msg="Ход не может быть применён к доске", move_success=False
            )
            return

        # высылаем телеметрию
        await send_telemetry(
            move_notation, to_sq, robot_state.current_position, "empty",
            data_msg="Ход успешно выполнен", move_success=True
        )

    except Exception as e:
        await send_telemetry(
            move_notation, None, robot_state.current_position, "error",
            error_msg=f"Внутренняя ошибка: {str(e)}", move_success=False
        )
    finally:
        async with robot_state.lock:
            robot_state.current_move_notation = None

@router.post("/code", status_code=status.HTTP_202_ACCEPTED)
async def receive_command(command: MoveCommand, background_tasks: BackgroundTasks):
    """Принимает ход, проверяет легальность и запускает эмуляцию."""

    async with robot_state.lock:
        if robot_state.current_move_notation is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Робот уже выполняет ход {robot_state.current_move_notation}"
            )


    if not is_legal_move(command.move_notation):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ход {command.move_notation} нелегален в текущей позиции"
        )

    background_tasks.add_task(emulate_move, command.move_notation)
    return {"status": "accepted", "message": f"Ход {command.move_notation} принят"}

@router.get("/status")
async def get_status():
    async with robot_state.lock:
        return {
            "position": robot_state.current_position.model_dump(),
            "gripper_status": robot_state.gripper_status,
            "current_move": robot_state.current_move_notation,
            "fen": get_board_fen()
        }

@router.post("/reset")
async def reset_robot():
    from chess_logic import reset_board
    async with robot_state.lock:
        robot_state.reset()
        reset_board()
    return {"status": "ok", "message": "Состояние робота и доски сброшено"}