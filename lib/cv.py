
from PIL import Image
import cv2 as cv
import numpy as np

class CvUser ():
    def __init__ (self, path=None):
        self.arg_min_value = 0
        self.arg_max_value = 255
        self.arg1_default = 50
        self.arg2_default = 100
        if path is not None:
            self.load_image(path)

    def load_image (self, path):
        image = cv.imread(path)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        r0 = cv.GaussianBlur(gray,
                             (5, 5),
                             0.83333)

        self.material = r0

    def apply_parameters (self, canny1p, canny2p):

        return Image.fromarray(cv.Canny(self.material,
                                        canny1p,
                                        canny2p))
