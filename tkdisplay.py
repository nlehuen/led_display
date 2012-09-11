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
    def __init__(self):
        self.root = Tk()
        self.label = Label(self.root, text = "Hello, world !")
        self.label.pack()
        self.img = None

        # Launch main loop
        self.mainLoop = threading.Thread(name="TkLoop", target=self.root.mainloop)
        self.mainLoop.start()

    def send_image(self, img):
        img = img.resize((320, 160))
        self.img = ImageTk.PhotoImage(img)
        self.label.config(image = self.img)