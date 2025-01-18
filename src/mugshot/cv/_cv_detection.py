from mugshot.mouse_input._frame_input import FrameInput


class CVDetection:
    def __init__(self): ...

    def process_frame(
        self, frame: cv2.typing.MatLike
    ) -> tuple[cv2.typing.MatLike, FrameInput]: ...
