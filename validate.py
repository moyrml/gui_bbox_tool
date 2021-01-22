import cv2
import argparse
from pathlib import Path
import pickle
import numpy as np


def create_annotated_image(file_path, bboxes, output_folder):
    img = cv2.imread(file_path).astype(np.uint8)

    for bbox in bboxes:
        bbox = list(bbox)
        img = cv2.rectangle(
            img,
            tuple(bbox[:2]),
            tuple([bbox[0] + bbox[2], bbox[1] + bbox[3]]),
            (255, 0, 0),
            2
        )

    cv2.imwrite(str(output_folder / Path(file_path).name), img)


def iterate_files(annotations, output_folder):
    for file_path, bboxes in annotations.items():
        create_annotated_image(file_path, bboxes, output_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='test_images')
    args = parser.parse_args()

    dir = Path(args.dir)

    if not dir.exists():
        raise FileNotFoundError('dir does not exist!')

    annotations_file = dir / 'results.pkl'

    if not annotations_file.exists():
        raise FileNotFoundError('Annotations cannot be found')

    with open(annotations_file, 'rb') as f:
        annotations = pickle.load(f)

    output_folder = dir / 'annotated'
    if not output_folder.exists():
        output_folder.mkdir(parents=True)

    iterate_files(annotations, output_folder)

