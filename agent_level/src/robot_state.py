import asyncio
from typing import Optional
from models import GripperPosition

class RobotState:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.current_position = GripperPosition(x=3.5, y=3.5)
        self.gripper_status = "empty"
        self.current_move_notation: Optional[str] = None

    def reset(self):
        self.current_position = GripperPosition(x=3.5, y=3.5)
        self.gripper_status = "empty"
        self.current_move_notation = None

robot_state = RobotState()