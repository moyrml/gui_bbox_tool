from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPixmap, QPen


class eventedLabel(QLabel):
    def __init__(self, parent_dim):
        """
        This class inherits the QPixmap class and handles events internally. It handles all the intra-image events.
        I keep an unmodified version of the original image in the background.
        :param parent_dim: Tuple. The dimensions of the parent window
        """
        super().__init__()
        self.mouse_held = False
        self.press_location = (None, None)

        self.scale_factor = (1, 1)
        self.parent_height = parent_dim[0]
        self.parent_width = parent_dim[1]

        self.existing_rects = []

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.mouse_held = True
        self.press_location = (event.pos().x(), event.pos().y())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        self.appendRect(
            *self.press_location,
            event.pos().x() - self.press_location[0],
            event.pos().y() - self.press_location[1]
        )

        self.drawExistingRects()
        self.mouse_held = False

    def appendRect(self, x, y, w, h):
        if w < 0:
            x = x + w
            w = abs(w)
        if h < 0:
            y = y + h
            h = abs(h)

        self.existing_rects.append([x, y, w, h])
        return x, y, w, h

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        self.drawTempRect(
            *self.press_location,
            event.pos().x() - self.press_location[0],
            event.pos().y() - self.press_location[1],
            Qt.red
        )

    def drawRect(self, x, y, w, h, c):
        self.painter = QPainter(self.pixmap)
        pen = QPen(c, 3)
        self.painter.setPen(pen)
        self.painter.drawRect(x, y, w, h)
        self.painter.end()
        self.setScaledPixmap()

    def drawTempRect(self, x, y, w, h, c):
        """
        This function draw a regtangle and clears it right up again. It is needed
        so that we dont start painting with rectangles on the image.

        :param c: QT constant. Color.
        :return:
        """
        self.drawRect(x, y, w, h, c)
        self.pixmap = self.static_pixmap.copy()

    def drawExistingRects(self):
        self.setScaledPixmap()
        for rect in self.existing_rects:
            self.drawRect(*rect, Qt.blue)

    def setImage(self, path, annotations):
        """
        Sets an image within the label and handle its annotations.
        :param path: Str. Path to the image file
        :param annotations: List of Lists. Bounding Box annotations of head location.
        [[x1,y1,w1,h1],
        [x2,y2,w2,h2]]

        :return: True if image loaded correctly. False otherwise.
        """
        self.existing_rects = []
        self.scale_factor = (1, 1)
        self.path = path
        self.pixmap = QPixmap(
            str(
                path
            )
        )

        if self.pixmap.isNull():
            print(f'Cannot load {str(path)}')
            return False

        self.setScaledPixmap()
        self.static_pixmap = self.pixmap.copy()

        if len(annotations) > 0:
            self.existing_rects = self.useAnnotations(annotations)
        self.drawExistingRects()

        return True

    def setScaledPixmap(self):
        if self.pixmap.height() > self.parent_height or self.pixmap.width() > self.parent_width:
            original_size = self.pixmap.height(), self.pixmap.width()
            self.pixmap = self.pixmap.scaled(self.parent_width, self.parent_height, Qt.KeepAspectRatio)

            self.scale_factor = (original_size[0] / self.pixmap.height(), original_size[1] / self.pixmap.width())

        self.setPixmap(self.pixmap)

    def labelToImageCoordinates(self, x, y, w, h):
        """
        Translate between label coordinates (possibly scaled to fit the screen) and image coordinates.
        :return: xywh in image coordinates
        """
        x *= self.scale_factor[0]
        y *= self.scale_factor[1]

        w *= self.scale_factor[0]
        h *= self.scale_factor[1]

        return x, y, w, h

    def imageToLabelCoordinates(self, x, y, w, h):
        """
        Translate between image coordinates and label coordinates (possibly scaled to fit the screen).
        :return: xywh in label coordinates
        """
        x /= self.scale_factor[0]
        y /= self.scale_factor[1]

        w /= self.scale_factor[0]
        h /= self.scale_factor[1]

        return x, y, w, h

    def getAnnotations(self):
        """
        Parse annotations to the activating class.
        :return: Annotaions in image coordinates.
        """
        return [list(map(round, self.labelToImageCoordinates(*coords))) for coords in self.existing_rects]

    def useAnnotations(self, annotations):
        """
        Parse annotations from file.
        :param annotations: List of lists.
        :return: List of lists.
        """
        return [self.imageToLabelCoordinates(*coords) for coords in annotations]

    def deleteAndUpdate(self):
        self.existing_rects = self.existing_rects[:-1]
        self.setImage(self.path, self.getAnnotations())
        self.drawExistingRects()
