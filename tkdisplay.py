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
        self._scale = scale
        self._resize = (size[0] * scale, size[1] * scale)

        # This queue will hold at most 1 image to paint
        self._queue = deque(maxlen=1)

        # Create GUI
        self._root = Tk()
        self._root.title("Emulator")
        self._canvas = Canvas(
            self._root,
            width = self._resize[0],
            height = self._resize[1]
        )
        self._canvas.pack()

        # Set the update loop to start as soon
        # as the main loop is launched
        self._root.after(0, self._update)

        # Set the window closed handler
        self._closed = False
        self._root.protocol("WM_DELETE_WINDOW", self.close)

        # Launch main loop
        self._mainLoop = threading.Thread(name="TkLoop", target=self._root.mainloop)
        self._mainLoop.start()

    def size(self):
        return self._size

    def send_image(self, img):
        if self._closed:
            # It's a bit of a hack but after all, closing the window
            # could be done through the keyboard :)
            raise KeyboardInterrupt("Emulator was closed")

        if self._scale != 1:
            img = img.resize(self._resize)

        self._queue.append(img)

    def close(self):
        self._closed = True
        self._root.quit()

    def _update(self):
        try:
            # Get the image to paint
            img = self._queue.popleft()

            # Create PhotoImage from PIL image
            img = ImageTk.PhotoImage(img)

            # Update the label
            self._canvas.create_image(0, 0, image = img, anchor = NW)

            # Keep a reference to the image in the label
            self._canvas._image = img
        except IndexError:
            pass

        # Loop within the Tkinter main loop
        # 100 FPS max
        self._root.after(10, self._update)