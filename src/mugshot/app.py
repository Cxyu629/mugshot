import logging
import sys
import time
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QImage, QPixmap
import cv2

from mugshot.mouse_input import FrameInput
from mugshot.cv import CVWorker
from mugshot.feed import FeedWorker


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        logging.info(f"Starting MainWindow initialization at {time.ctime()}")

        # === Widget states ===
        self.isDoingInputs = False

        # === Set up window widgets ===
        layout = QVBoxLayout()

        # Initialize camera feed widget
        self.feed = Feed()
        layout.addWidget(self.feed)

        # Initialize start/stop button widget
        self.startStopBtn = StartStopBtn()
        layout.addWidget(self.startStopBtn)

        # Set QWidget properties after initializing component widgets
        self.setWindowTitle("MUGSHOT")
        self.setLayout(layout)

        # === Initialize threads ===
        self.cvWorker = CVWorker()
        self.feedWorker = FeedWorker()

        # === Set up signal flow ===
        self.feedWorker.frameRead.connect(self.cvWorker.processFrame)
        self.cvWorker.frameProcessed.connect(self.feed.setFeed)
        self.cvWorker.inputsMade.connect(self.doInputs)

    def doInputs(self, frameInput: FrameInput):
        # TODO: Process and do inputs
        ...


class Feed(QLabel):
    SIZE = QSize(640, 480)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeHolderImage = QImage(self.SIZE, QImage.Format.Format_BGR888)
        placeHolderImage.fill(Qt.GlobalColor.lightGray)
        self.setPixmap(QPixmap.fromImageInPlace(placeHolderImage))

    def setFeed(self, frame: cv2.typing.MatLike):
        image = QImage(
            frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888
        )
        image = image.scaled(self.SIZE, Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(image)


class StartStopBtn(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCheckable(True)
        self.toggled.connect(self.changeText)
        self.changeText(False)

    def changeText(self, checked):
        if checked:
            self.setText("Stop")
        else:
            self.setText("Start")


class App:
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._root = MainWindow()

    def run(self):
        self._root.show()
        self._app.exec()
