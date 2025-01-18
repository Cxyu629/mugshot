from abc import ABC
from mugshot.mouse_input import FrameInput
import cv2


class BaseCVDetection(ABC):
    """An abstract base class for implementing CV detection."""

    def process_frame(
        self, frame: cv2.typing.MatLike
    ) -> tuple[cv2.typing.MatLike, FrameInput]:
        """Processes a BGR frame and returns an annotated frame and inputs to be executed.

        Arguments:
        - `frame`: cv2.Mat -- A 24-bit BGR image

        Returns:
        - A tuple of `(cv2.Mat, FrameInput)`, referring respectively to an annotated frame and the corresponding inputs to be executed.
        """
        ...
