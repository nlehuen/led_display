# -*- coding: utf-8 -*-

import serial
import traceback

class Display(object):
    def __init__(self, port='COM6:', baudrate=2000000):
        self._serial = serial.Serial(port, baudrate, timeout=1)
        self._matrix_command = [chr(2), chr(1)]

    def size(self):
        return (32, 16)

    def send_image(self, img):
        if img.size != (32, 16):
            img = img.crop((0, 0, 32, 16))
        data = self._matrix_command
        data = data + [(value==2 and chr(3) or chr(value)) for pixel in img.getdata() for value in pixel]
        data = "".join(data)
        if self._serial is not None:
            self._serial.write(data)
