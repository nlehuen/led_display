# -*- coding: utf-8 -*-
import threading

try:
    # in case of easy_installed PIL
    import ImageTk
except ImportError:
    # in case of distribution or windows PIL
    from PIL import ImageTk

from Tkinter import *

class Display(object):
    def __init__(self, size=(32,16)):
        self._size = size
        self._resize = (size[0] * 8, size[1] * 8)

        self._root = Tk()
        self._label = Label(self._root, text = "Hello, world !")
        self._label.pack()
        self._img = None

        # Launch main loop
        self._mainLoop = threading.Thread(name="TkLoop", target=self._root.mainloop)
        self._mainLoop.start()

    def size(self):
        return self._size

    def send_image(self, img):
        img = img.resize(self._resize)
        self._img = ImageTk.PhotoImage(img)
        self._label.config(image = self._img)