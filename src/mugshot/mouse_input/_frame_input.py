from dataclasses import dataclass
from typing import Optional


@dataclass
class FrameInput:

    is_left_eye_closed: bool = False
    is_right_eye_closed: bool = False
    cursor_pos: Optional[tuple[float, float]] = None
