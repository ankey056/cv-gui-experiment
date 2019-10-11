#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ttk
from ttk import Tkinter as tk
import tkFileDialog
import sys
from lib.zoom import ViewPort
from lib.cv import CvUser

class App(ttk.Frame):
    def __init__ (self, path, master=None):
        ttk.Frame.__init__(self, master)
        self.cv_user = CvUser(path)
        self.__init_tk_vars()
        self.master.title(path)
        self.saving_filename = None
        scaleInitArgs = {'from_':self.cv_user.arg_min_value,
                         'to':self.cv_user.arg_max_value,
                         'orient':ttk.Tkinter.VERTICAL}
        scale1 = ttk.Scale(self, variable=self.canny1,
                           command=self.__updating_parameters_cb,
                           **scaleInitArgs)
        scale2 = ttk.Scale(self, variable=self.canny2,
                           command=self.__updating_parameters_cb,
                           **scaleInitArgs)
        self.scale1 = scale1
        self.scale2 = scale2

        view_port = ViewPort(self,
                             self.cv_user.apply_parameters(self.canny1.get(),
                                                           self.canny2.get()))
        self.view_port = view_port
        self.canvas = view_port.canvas
        self.__bottom_frame = ttk.Frame(self)
        lab = ttk.Label(self.__bottom_frame,
                        text="Everything is OK", justify=tk.LEFT)
        self.label = lab
        self.__rb_frame = ttk.Frame(self.__bottom_frame)

        modes = (("Normal", 0),
                 ("Stretched", 1),
                 ("Proportional", 2))

        l = list()
        for text, v in modes:
            b = ttk.Radiobutton(self.__rb_frame, text=text,
                                variable=self.view_port.zoom_mode_var,
                                value=v, command=self.__update_rb_ui)
            l.append(b)
        self.__rb_list = l

        self.__arrange_widgets()
        self.__bind_events()
        # self.__update_statusLab()
        self.focus_set()

    def __init_tk_vars (self):
        self.canny1 = tk.IntVar(value=self.cv_user.arg1_default)
        self.canny2 = tk.IntVar(value=self.cv_user.arg2_default)

    def __arrange_widgets(self):
        self.grid(row=0, column=0, sticky="NESW")
        self.scale1.grid(column=0, row=0, sticky="WNS")
        self.scale2.grid(column=1, row=0, sticky="WNS")
        self.canvas.grid(column=2, row=0, sticky="WNES")#+tk.N+tk.S)
        bframe = self.__bottom_frame
        bframe.grid(column=0, row=1, sticky="WES", columnspan=3)
        rb_frame = self.__rb_frame
        rb_frame.grid(column=1, row=0, sticky="NES")
        self.label.grid(row=0, column=0, sticky="WS")
        i=0
        for rb in self.__rb_list:
            rb.grid(row=i, column=0, sticky="WS")
            i+=1

        root = self._nametowidget(self.winfo_parent())
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(self, 2, weight=1)
        tk.Grid.columnconfigure(self.__bottom_frame, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)


    def __bind_events (self):
        self.bind("o", self.__open_image_cb)
        self.bind("S", self.__save_image_dialog_cb)
        self.bind("<Control-s>", self.__save_image_cb)
        self.bind("z", self.view_port.zoom)
        self.bind("Z", self.view_port.change_zoom_mode)

    def __update_rb_ui (self):
        self.view_port.reload_zoom_method()
        self.focus_set()

    def __open_image_cb (self, ev):
        path = tkFileDialog.askopenfilename()
        self.master.title(path)
        if len(path) > 0:
            self.cv_user.load_image(path)
            self.__updating_parameters_cb(None)

    def save_image (self, path):
        self.view_port.image.save(path , "PNG")
        self.label['text'] = "Image successfully saved in {}".format(path)

    def __save_image_cb (self, ev):
        if self.saving_filename is None:
            self.__save_image_dialog_cb(ev)
        else:
            self.save_image(self.saving_filename)

    def __save_image_dialog_cb (self, ev):
        filetypes = (("PNG files", "*.png"),
                     ("All files", "*.*"))
        path = tkFileDialog.asksaveasfilename(filetypes=filetypes)
        if len(path) != 0:
            self.save_image(path)
            self.saving_filename = path

    def __update_statusLab (self):
        fmt = "cv.Canny(gray_image, {}, {})"
        self.label['text'] = fmt.format(self.canny1.get(),
                                        self.canny2.get())

    def __updating_parameters_cb (self, x):
        img = self.cv_user.apply_parameters(self.canny1.get(),
                                            self.canny2.get())
        self.view_port.update(img)
        self.__update_statusLab()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = tkFileDialog.askopenfilename()

    if len(path) > 0:
        app = App(path)

        app.update()

        app.mainloop()

