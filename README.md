# GUI Bounding Box Tool

This repository contains code for GUI bounding box application. 

## Installation 
Code was developed on Linux Kubuntu 18.04, Python 3.7.1, PyQt5.
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Use
```bash
python main.py --dir /path/to/images/folder
```

All keyboard shortcuts and gestures according to spec received.
The program saves a pickle file to the directory specified.
The program prints messages to the console. 

## Validation
Extra validation code is provided. It is built upon python-opencv.
```bash
python validate.py --dir /path/to/images/folder
``` 
It creates a directory 'Annotated' in the directory specified, saves all images with the BBs painted on top and exists.

