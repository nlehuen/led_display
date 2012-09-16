# -*- coding: utf-8 -*-
import threading

try:
    # in case of easy_installed PIL
    import ImageTk
except ImportError:
    # in case of distribution or windows PIL
    from PIL import ImageTk

from collections import deque
from Tkinter import *

class Display(object):
    def __init__(self, size, scale):
        self._size = size
        if scale != 1:
            self._resize = (size[0] * scale, size[1] * scale)
        else:
            self._resize = None

        # This queue will hold at most 1 image to paint
        self._queue = deque(maxlen=1)

        # Create GUI
        self._root = Tk()
        self._root.title("Emulator")
        self._label = Label(self._root, text = "Hello, world !")
        self._label.pack()

        # Set the update loop to start as soon
        # as the main loop is launched
        self._root.after(0, self._update)

        # Launch main loop
        self._mainLoop = threading.Thread(name="TkLoop", target=self._root.mainloop)
        self._mainLoop.start()

    def size(self):
        return self._size

    def send_image(self, img):
        if self._resize is not None:
            img = img.resize(self._resize)

        self._queue.append(ImageTk.PhotoImage(img))

    def _update(self):
        try:
            # Get the image to paint
            img = self._queue.popleft()

            # Update the label
            self._label.config(image = img)

            # Keep a reference to the image in the label
            self._label._image = img
        except IndexError:
            pass

        # Loop within the Tkinter main loop
        self._root.after(20, self._update) # 50 FPS