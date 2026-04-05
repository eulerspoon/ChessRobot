import chess
from typing import Optional

_board = chess.Board()

def get_board_fen() -> str:
    return _board.fen()

def is_legal_move(move_notation: str) -> bool:
    """Проверяет, легален ли ход в текущей позиции."""
    try:
        move = chess.Move.from_uci(move_notation)
        return move in _board.legal_moves
    except ValueError:
        return False

def apply_move(move_notation: str) -> bool:
    """Применяет ход к доске. Возвращает True, если успешно."""
    try:
        move = chess.Move.from_uci(move_notation)
        if move not in _board.legal_moves:
            return False
        _board.push(move)
        return True
    except Exception:
        return False

def reset_board():
    _board.reset()