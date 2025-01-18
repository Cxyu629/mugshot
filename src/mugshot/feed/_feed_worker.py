import sys
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import cv2


# Thread for camera feed
class feedWorker(QThread):
    imageUpdate = Signal(QImage)

    # Run Thread
    def run(self):
        self.threadActive = True
        self.capture = cv2.VideoCapture(0)
        while self.threadActive:
            ret, frame = self.capture.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # flip image to mirror
                flippedImage = cv2.flip(image, 1)
                convertToQtFormat = QImage(flippedImage.data, flippedImage.shape[1], flippedImage.shape[0], QImage.Format.Format_RGB888)
                pic = convertToQtFormat.scaled(640, 480, QSize.KeepAspectRatio)
                self.imageUpdate.emit(pic)

    # Stop Thread
    def stop(self):
        self.ThreadActive = False
        self.capture.release()