# -*- coding: utf-8 -*-

from enum import Enum
from ttk import Tkinter as tk
from PIL import ImageTk


def image_size (image):
    x = (image.width,
         image.height)
    return x


class ZoomMode (Enum):
    Normal = 0
    Stretched = 1
    Proportional = 2

    @staticmethod
    def normal_method (op_rect, av_size, img_size):
        return op_rect, img_size

    @staticmethod
    def stretch_method (op_rect, av_size, img_size):
        return op_rect, av_size

    @staticmethod
    def proportional_stretch_method (op_rect, av_size, img_size):
        w, h = av_size
        p = float(w)/h
        if op_rect is None:
            x01 = 0
            y01 = 0
            x02 = img_size[0]
            y02 = img_size[1]
        else:
            x01, y01, x02, y02 = op_rect

        rw = x02 - x01
        rh = y02 - y01

        pw = rh*p

        if pw <= rw:
            x1 = x01
            x2 = x02
            dy = round((rw/p-rh)/2)
            y1 = y01-dy
            y2 = y02+dy
        else:
            y1 = y01
            y2 = y02
            dx = round((pw-rw)/2)
            x1 = x01-dx
            x2 = x02+dx

        return (x1, y1, x2, y2), av_size

    @staticmethod
    def get_method (m):
        _mtable = {ZoomMode.Normal: ZoomMode.normal_method,
                   0: ZoomMode.normal_method,
                   ZoomMode.Stretched: ZoomMode.stretch_method,
                   1: ZoomMode.stretch_method,
                   ZoomMode.Proportional: ZoomMode.proportional_stretch_method,
                   2: ZoomMode.proportional_stretch_method}

        return _mtable[m]

class ViewPort ():


    def __init__ (self, frame, image):
        self.image = image
        image = ImageTk.PhotoImage(image)
        w = image.width()
        h = image.height()
        canvas = tk.Canvas(frame, width=w, height=h)
        canvas.imageobj = canvas.create_image(0.5*w,0.5*h,image=image)
        canvas.image=image
        self.vision_size = (w, h)
        self.canvas = canvas
        self.__rect_tracker = RectTracker(canvas)
        self.__operational_rect = None
        self.zoom_mode_var = tk.IntVar()
        self.set_zoom_mode(ZoomMode.Normal)
        self.__orig_size = self.vision_size

    def upload_image (self, image):
        canvas = self.canvas
        canvas.itemconfig(canvas.imageobj, image=image)
        canvas.image=image

    def image_reposition (self, oldpos, pos):
        canvas = self.canvas
        moving = map(lambda o, p: p-o,
                     oldpos,
                     pos)
        canvas.move(canvas.imageobj, *moving)

    def perform_zoom (self, image_size):
        if image_size != self.vision_size:
            x = map(lambda l: map(lambda c: c*0.5, l),
                    self.vision_size,
                    image_size)
            self.image_reposition(*x)
            self.vision_size = image_size

    def get_zoom_mode (self):
        return ZoomMode(self.zoom_mode_var.get())

    def set_zoom_mode (self, mode):
        self.zoom_mode_var.set(mode.value)
        self.reload_zoom_method()

    def reload_zoom_method (self):
        self.zoom_method = ZoomMode.get_method(self.get_zoom_mode())

    def update (self, image):
        if image is None:
            image = self.image
        else:
            self.image = image
            self.__orig_size = image_size(image)

        img_size = self.__orig_size
        op_rect = self.__operational_rect

        if op_rect is not None:
            image = image.crop(op_rect)
            img_size = image_size(image)

        vsize = self.vision_size
        if vsize != img_size:
            image = image.resize(vsize)
            img_size = vsize


        image = ImageTk.PhotoImage(image)
        self.upload_image(image)

    def possible_max_vision_size (self):
        c = self.canvas
        l = map(lambda x: x-2,
                [c.winfo_width(),
                 c.winfo_height()])
        return tuple(l)

    def zoom (self, ev=None):
        r = self.__rect_tracker.rectc
        if r is None:
            self.__operational_rect = None
        else:
            r = ViewPort.adapte_rect(r)
            self.__update_operation_rect(r)

            self.__rect_tracker.clean()

        op_rect, size = self.zoom_method(self.__operational_rect,
                                         self.possible_max_vision_size(),
                                         self.__orig_size)

        self.__operational_rect = op_rect

        if size != self.vision_size:
            x = map(lambda l: map(lambda c: c*0.5, l),
                    (self.vision_size,
                     size))
            self.image_reposition(*x)
            self.vision_size = size # image_size()

        self.update(None)

    def __update_operation_rect (self, rect):
        # w, h = vision_size
        vision_size = self.vision_size
        if self.__operational_rect is None:
            if vision_size == self.__orig_size:
                self.__operational_rect = rect
                return

            else:
                x1 = 0
                y1 = 0
                ims = self.__orig_size
        else:
            x1, y1, x2, y2 = self.__operational_rect
            ims = ((x2 - x1),
                   (y2 - y1))

        wr, hr = map(lambda so, sv: float(so)/sv,
                     ims,
                     vision_size)


        xi1, yi1, xi2, yi2 = rect

        r = map(round,
                ((xi1*wr+x1),
                 (yi1*hr+y1),
                 (xi2*wr+x1),
                 (yi2*hr+y1)))
        self.__operational_rect = r


    @staticmethod
    def adapte_rect (rectc):
        x1, y1, x2, y2 = rectc
        if x1 > x2: x1, x2 = x2, x1
        if y1 > y2: y1, y2 = y2, y1
        return (x1, y1, x2, y2)


    def change_zoom_mode (self, ev):
        mode = self.get_zoom_mode()
        self.set_zoom_mode(ZoomMode((mode.value+1) % 3))
        # self.zoom_mode_var.set((mode.value+1) % 3)


class RectTracker:

    def __init__(self, canvas):
        self.canvas = canvas
        self.items = None
        self.start = None
        self.rectc = None
        self.canvas.bind("<Button-1>", self.__update, '+')
        self.canvas.bind("<B1-Motion>", self.__update, '+')
        self.canvas.bind("<ButtonRelease-1>", self.__stop, '+')
        self.canvas.bind("<Button-3>", self.__clean_cb)#, '+')


    def draw (self, start, end):
        """Draw the rectangle"""
        args = list(start)+list(end)
        x = (self.canvas.create_rectangle(*args,
                                          outline='white',
                                          width=3,
                                          dash=(8, 6)),
             self.canvas.create_rectangle(*args,
                                          outline='black',
                                          width=1,
                                          dash=(8, 6)))
        return x

    def __update(self, event):
        if not self.start:
            self.start = [event.x, event.y]
            return

        if self.items is not None:
            map(self.canvas.delete, self.items)
        self.items = self.draw(self.start, (event.x, event.y))
        self.rectc = self.start + [ event.x, event.y]
               # self._command(self.start, (event.x, event.y))

    def __stop(self, event):
        self.start = None
        # map(self.canvas.delete, self.items)
        # self.items = None

    def __clean_cb(self, event):
        self.clean()

    def clean(self):
        self.start = None
        if self.items is not None:
            map(self.canvas.delete, self.items)
        self.items = None
        self.rectc = None
