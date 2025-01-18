import logging
import sys
import time
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QImage, QPixmap
import cv2

from mugshot.cv import AltCVDetection
from mugshot.mouse_input import FrameInput
from mugshot.cv import CVWorker
from mugshot.feed import FeedWorker
from mugshot.mouse_input import MouseAction
from mugshot.mouse_input import Screen


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        logging.info(f"Initializing MainWindow at {time.ctime()}")

        # === Widget states ===
        self.isDoingInputs = False

        # === Set up window widgets ===
        layout = QVBoxLayout()

        # Initialize camera feed widget
        self.feed = Feed()
        layout.addWidget(self.feed)

        # Initialize start/stop button widget
        self.startStopBtn = StartStopBtn()
        self.startStopBtn.toggled.connect(self.setDoingInputs)
        layout.addWidget(self.startStopBtn)

        # Set QWidget properties after initializing component widgets
        self.setWindowTitle("MUGSHOT")
        self.setLayout(layout)

        # === Initialize threads ===
        self.cvWorker = CVWorker(cv_detection_class=AltCVDetection)
        self.feedWorker = FeedWorker()

        # === Set up signal flow ===
        self.feedWorker.frameRead.connect(self.cvWorker.processFrame)
        self.cvWorker.frameProcessed.connect(self.feed.setFeed)
        self.cvWorker.inputsMade.connect(self.doInputs)

        # === Start threads ===
        self.cvWorker.start()
        self.feedWorker.start()

        logging.info(f"Finished initializing MainWindow at {time.ctime()}")

    def setDoingInputs(self, value):
        if not value and not value == self.isDoingInputs:
            MouseAction.left_up()
            MouseAction.right_up()

        self.isDoingInputs = value

    def doInputs(self, frameInput: FrameInput):
        """Public slot for executing inputs."""

        if self.isDoingInputs:
            if frameInput.is_left_eye_closed is not None:
                if frameInput.is_left_eye_closed:
                    MouseAction.left_down()
                else:
                    MouseAction.left_up()

            if frameInput.is_right_eye_closed is not None:
                if frameInput.is_right_eye_closed:
                    MouseAction.right_down()
                else:
                    MouseAction.right_up()

            if frameInput.cursor_pos is not None:
                width, height = Screen.get_size()
                new_cursor_pos = (
                    int(frameInput.cursor_pos[0] * width),
                    int(frameInput.cursor_pos[1] * height),
                )
                MouseAction.move_to(*new_cursor_pos)

            if frameInput.is_tongue_down is not None:
                if frameInput.is_tongue_down:
                    MouseAction.v_scroll(-100)
                else:
                    MouseAction.v_scroll(100)

    def paintEvent(self, event):
        """Overrides QWidget.paintEvent, reads successive frames in a loop."""

        if self.feedWorker.capture is not None:
            self.feedWorker.readFrame()
        super().paintEvent(event)

    def closeEvent(self, event):
        """Overrides QWidget.closeEvent, cleans up worker resources."""

        self.feedWorker.quit()
        self.cvWorker.quit()
        super().closeEvent(event)


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
        self.setPixmap(QPixmap.fromImage(image))


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
