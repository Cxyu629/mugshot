from dataclasses import dataclass
import logging
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
        self.rect = Rectangle(0, 0, 0, 0)
        self.width = 0
        self.height = 0

    # Run Thread
    def run(self):
        """Overrides QThread.run(). Initializes a cv2.VideoCapture object asynchronously, and kickstarts an update loop.

        The initialization takes a few seconds."""
        if self.capture == None:
            self.capture = cv2.VideoCapture(0) # Slow operation (~ 3 secs)
            width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if self.width == 0 or self.height == 0:
                self.rect.x2 = width
                self.rect.y2 = height
            self.width = width
            self.height = height

        self.readFrame() # Call once to kickstart update loop (readFrame -> repaint -> readFrame -> ...)

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
        flippedImage = cv2.flip(frame, 1)
        rectOverlay = cv2.rectangle(flippedImage, (self.rect.x1, self.rect.y1), (self.rect.x2, self.rect.y2), (0, 0, 0), -1)
        self.frameRead.emit(rectOverlay)

    # def rectChanged(self):


    # Stop Thread
    def quit(self):
        """ Overrides QThread.quit() to clean up 'cv2.videoCapture' object."""
        if self.capture is not None:
            self.capture.release()
        super().quit()

@dataclass
class Rectangle:
    x1:int
    y1:int
    x2:int
    y2:int

