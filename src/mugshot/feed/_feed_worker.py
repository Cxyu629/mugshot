import logging
import time
from PySide6.QtCore import QThread, Signal
import cv2


# Thread for camera feed
class FeedWorker(QThread):
    """A worker thread for camera feed.

    Public signals:
    - `frameRead`: Signal(cv2.Mat) -- Indicates that a frame is read, and emits that frame

    Public slots:
    - `readFrame`: function(frame: cv2.Mat) -- Read a frame, then emits signal `frameRead`
    """

    # Public signal to indicate that a frame has been read and emits that frame
    frameRead = Signal(cv2.Mat)

    def __init__(self):
        super().__init__()
        self.capture = None

    # Run Thread
    def run(self):
        """Overrides QThread.run(). Initializes a cv2.VideoCapture object asynchronously, and kickstarts an update loop.

        The initialization takes a few seconds."""

        logging.info(f"Initializing VideoCapture in FeedWorker at {time.ctime()}")
        if self.capture == None:
            self.capture = cv2.VideoCapture(0)  # Slow operation (~ 3 secs)

        self.readFrame()  # Call once to kickstart update loop (readFrame -> repaint -> readFrame -> ...)

    def readFrame(self):
        """Public slot to read from a camera."""

        assert self.capture != None

        # Checks if camera is not open
        if not self.capture.isOpened():
            logging.error("Video capture is not opened")
            return

        # ret (boolean) indicates whether frame was successfully read
        ret, frame = self.capture.read()
        if not ret:
            logging.error("Failed to read frame")
            return

        # Emits flipped image to mirror user
        self.frameRead.emit(cv2.flip(frame, 1))

    # Stop Thread
    def quit(self):
        """Overrides QThread.quit() to clean up 'cv2.videoCapture' object."""

        if self.capture is not None:
            self.capture.release()
        super().quit()
