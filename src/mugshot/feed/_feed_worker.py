import logging
from PySide6.QtCore import QThread, Signal
import cv2


# Thread for camera feed
class FeedWorker(QThread):
    
    # Worker thread relaying camera feed to GUI.
    
    # Public signal to indicate that a frame has been read and emits that frame
    frameRead = Signal(cv2.Mat)

    def __init__(self):
        super().__init__()
        self.capture = None

    # Run Thread
    def run(self):
        if self.capture == None:
            self.capture = cv2.VideoCapture(0)

        self.readFrame()

    # Public slot that reads a frame, then emits signal 'frameRead'
    def readFrame(self):
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

        # Overrides QThread.quit() to clean up 'cv2.videoCapture' object
        if self.capture is not None:
            self.capture.release()
        super().quit()