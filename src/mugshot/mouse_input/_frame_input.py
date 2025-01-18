from dataclasses import dataclass
from typing import Optional


@dataclass
class FrameInput:
    """A dataclass for storing to-be-executed inputs recorded with CV."""

    is_left_eye_closed: Optional[bool] = None
    """`Optional[bool]`, whether the left eye is closed, None by default."""

    is_right_eye_closed: Optional[bool] = None
    """`Optional[bool]`, whether the right eye is closed, None by default."""

    cursor_pos: Optional[tuple[float, float]] = None
    """The nose position in a frame with type `Optional[tuple[float, float]]`.
    
    If the position is not None, (x=0.0, y=0.0) refers to the top-left corner, and (x=1.0, y=1.0) refers to the bottom-right corner."""

    is_tongue_out: Optional[bool] = None
    """`Optional[bool]`, whether the tongue is stuck out. None by default."""
