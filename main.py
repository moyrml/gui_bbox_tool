from pathlib import Path
import argparse

from PyQt5.QtWidgets import QApplication

from main_window import Window

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='test_images')
    args = parser.parse_args()

    dir = Path(args.dir)

    if not dir.exists():
        raise FileNotFoundError('dir does not exist!')

    img_list = list(dir.glob('*'))

    app = QApplication([])
    window = Window(args, img_list)

    app.exec_()
