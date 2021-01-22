from pathlib import Path
import pickle
from PyQt5.QtCore import Qt, QMimeDatabase
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
import numpy as np

from image_label import eventedLabel

class Window(QMainWindow):
    def __init__(self, args, img_list):
        """
        This is the main window class. It handles all the inter-image events.
        :param args: Argparse object. Command line arguments.
        :param img_list: List of pathlib.Path.
        """
        super().__init__()
        self.args = args
        self.img_list = img_list
        self.current_image = -1
        self.annotations = {}

        if (Path(args.dir) / 'results.pkl').exists():
            with open(Path(args.dir) / 'results.pkl', 'rb') as f:
                self.annotations = pickle.load(f)

                # case where the user stopped half-way and the image isnt in the annotations dict at all
                mime_db = QMimeDatabase()
                unopened_image = [str(img) for img in self.img_list
                                  if str(img) not in self.annotations
                                  and 'image' in mime_db.mimeTypeForFile(str(img)).name()]
                unannotated_index = np.where([str(img) in unopened_image for img in self.img_list])[0]

                if len(unannotated_index) == 0:
                    self.current_image = len(self.img_list) - 1
                else:
                    self.current_image = unannotated_index - 1  # minus 1 because i add 1 at the beginning of nextImage

        self.initLayout()

        self.show()

    def initLayout(self):
        self.setWindowTitle("GUI head labeler")

        self.width = 1000
        self.height = 500

        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.image_label = eventedLabel([self.height, self.width])
        self.central_widget.setLayout(self.vbox)
        self.vbox.addWidget(self.image_label)

        self.nextImage()

    def nextImage(self, direction='next'):
        self.current_image = self.current_image + 1 if direction == 'next' else self.current_image - 1
        if direction == 'next' and self.current_image >= len(self.img_list):
            print('Reached the last image.')
            self.current_image = len(self.img_list) - 1
            return

        if direction == 'previous' and self.current_image < 0:
            print('Reached the first image.')
            self.current_image = 0
            return

        next_img_path = str(self.img_list[self.current_image])
        annotations = self.annotations.get(next_img_path, [])

        if not self.image_label.setImage(self.img_list[self.current_image], annotations):
            self.nextImage(direction)

    def getAnnotations(self):
        self.annotations[str(self.img_list[self.current_image])] = self.image_label.getAnnotations()

    def saveCurrentData(self):
        with open(Path(self.args.dir) / 'results.pkl', 'wb') as f:
            pickle.dump(self.annotations, f)
            print(f'Created pickle file {Path(self.args.dir) / "resutls.pkl"}')

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        key = event.key()
        if key == Qt.Key_Left:
            self.getAnnotations()
            self.nextImage('previous')
        elif key == Qt.Key_Right:
            self.getAnnotations()
            self.nextImage()
        elif key == Qt.Key_Q:
            self.getAnnotations()
            self.saveCurrentData()
            self.close()
        elif key == Qt.Key_S:
            self.saveCurrentData()
        elif key == Qt.Key_D:
            self.image_label.deleteAndUpdate()

