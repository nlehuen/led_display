# -*- coding: utf-8 -*-

import serial
import traceback
import threading
from Queue import Queue, Full

class Display(object):
    def __init__(self, port, speed, threaded):
        self._serial = serial.Serial(port, speed, timeout=1)

        if threaded:
            self._queue = Queue(1)
            self._thread = threading.Thread(name="LEDDisplay", target=self._run)
            self._thread.daemon = True
            self._thread.start()
        else:
            self._queue = None

    def size(self):
        return (32, 16)

    def send_image(self, img):
        # Crop source image if needed
        if img.size != (32, 16):
            img = img.crop((0, 0, 32, 16))

        # Encode image data (optimized code, thanks @jon1012)
        # Encoding is performed in the caller (i.e. the animator) thread
        # so that the image can be reused for the next frame
        data = '\x02\x01' + img.tostring("raw", "RGB").replace('\x02','\x03')

        if self._queue is None:
            # Directly send data
            self._serial.write(data)
        else:
            # Enqueue data
            try:
                self._queue.put(data, block=False)
            except Full:
                # Silently drops images if the screen cannot keep up
                pass

    def _run(self):
        while True:
            data = self._queue.get()
            self._serial.write(data)