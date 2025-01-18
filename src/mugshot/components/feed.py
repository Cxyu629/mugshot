from dataclasses import dataclass
from enum import Flag, auto
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QImage, QMouseEvent, QPixmap
import cv2
import numpy as np


@dataclass
class Rect:
    x1: int
    y1: int
    x2: int
    y2: int


@dataclass
class RectFloat:
    x1: float
    y1: float
    x2: float
    y2: float


class Border(Flag):
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()


class Feed(QLabel):
    SIZE = QSize(640, 480)

    mapAreaChanged = Signal(RectFloat)

    def __init__(self, *args, mapArea: RectFloat, **kwargs):
        super().__init__(*args, **kwargs)
        placeHolderImage = QImage(self.SIZE, QImage.Format.Format_BGR888)
        placeHolderImage.fill(Qt.GlobalColor.lightGray)
        self.setPixmap(QPixmap.fromImageInPlace(placeHolderImage))
        self.mapArea = Rect(
            int(mapArea.x1 * self.SIZE.width()),
            int(mapArea.y1 * self.SIZE.height()),
            int(mapArea.x2 * self.SIZE.width()),
            int(mapArea.y2 * self.SIZE.height()),
        )
        self.dragging = Border(0)

    def setFeed(self, frame: cv2.typing.MatLike):
        alpha = 0.6
        mask = np.zeros((self.SIZE.height(), self.SIZE.width(), 3), np.float32)
        mask.fill(alpha)
        topLeft = (self.mapArea.x1, self.mapArea.y1)
        bottomRight = (self.mapArea.x2, self.mapArea.y2)
        cv2.rectangle(mask, topLeft, bottomRight, (1.0, 1.0, 1.0), -1)

        dst = cv2.multiply(mask, frame.astype(np.float32)).astype(np.uint8)
        image = QImage(
            dst.data, dst.shape[1], dst.shape[0], QImage.Format.Format_BGR888
        )

        image = image.scaled(self.SIZE, Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(QPixmap.fromImage(image))

    def mouseMoveEvent(self, ev) -> None:
        if Border.LEFT in self.dragging:
            self.mapArea.x1 = int(ev.position().x())
        if Border.RIGHT in self.dragging:
            self.mapArea.x2 = int(ev.position().x())
        if Border.TOP in self.dragging:
            self.mapArea.y1 = int(ev.position().y())
        if Border.BOTTOM in self.dragging:
            self.mapArea.y2 = int(ev.position().y())
        return super().mouseMoveEvent(ev)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if abs(ev.position().x() - self.mapArea.x1) <= 5:
            self.dragging |= Border.LEFT
        if abs(ev.position().x() - self.mapArea.x2) <= 5:
            self.dragging |= Border.RIGHT
        if abs(ev.position().y() - self.mapArea.y1) <= 5:
            self.dragging |= Border.TOP
        if abs(ev.position().y() - self.mapArea.y2) <= 5:
            self.dragging |= Border.BOTTOM
        return super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.dragging = Border(0)
        self.mapAreaChanged.emit(
            RectFloat(
                self.mapArea.x1 / self.SIZE.width(),
                self.mapArea.y1 / self.SIZE.height(),
                self.mapArea.x2 / self.SIZE.width(),
                self.mapArea.y2 / self.SIZE.height(),
            )
        )
        return super().mouseReleaseEvent(ev)
