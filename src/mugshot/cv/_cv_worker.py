import logging
import time
from PySide6.QtCore import QThread, Signal
import cv2

from ._base_cv_detection import BaseCVDetection
from mugshot.mouse_input import FrameInput


class CVWorker(QThread):
    """A worker thread for cv."""

    frameProcessed = Signal(cv2.Mat)
    """Public signal `cv2.Mat` for an annotated frame."""

    inputsMade = Signal(FrameInput)
    """Public signal `FrameInput` for inputs to be executed."""

    def __init__(self, *args, cv_detection_class=BaseCVDetection, **kwargs):
        super().__init__(*args, **kwargs)
        self._cvDetectionClass = cv_detection_class
        self.cvDetection = None

    def run(self):
        """Overrides QThreads.run, initializes CV functionalities asynchronously"""
        if self.cvDetection is None:
            logging.info(f"Initializing CV detection at {time.ctime()}.")
            self.cvDetection = self._cvDetectionClass()
            logging.info(f"Finished initializing CV detection at {time.ctime()}.")

    def processFrame(self, frame: cv2.Mat):
        """Public slot to process frames."""

        if self.cvDetection is None:
            logging.error(f"Expected self.cvDetection to be initialized.")
            return

        annotatedFrame, frameInput = self.cvDetection.process_frame(frame)

        self.frameProcessed.emit(annotatedFrame)
        self.inputsMade.emit(frameInput)
