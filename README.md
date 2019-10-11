
# cv-gui-experiment

Python GUI framwork for experiments with OpenCV.

License: MIT

## Usage

```./gui.py <image-file>```

or with dialog window:

```./gui.py```

### Key bindings

+ 'o' - open file
+ 'S' - save image
+ 'Ctrl-s' - save image in new file
+ 'Z' - change zoom mode
+ 'z' - zoom

### Zoom usage

It is possible to allocate rectangle on the image by using mouse
dragging and activate zoom of allocated area by pressing 'z'
key. Option of changing zoom mode is available by the use of radio
button at bottom right corner of the window. Pressing 'z' key without
allocated rectangle returns initial full-size image on the window.

## Requirements

+ python 2.7
+ opencv2 (tested with opencv 2.4.13.6)
+ <https://python-pillow.org/>
