# -*- coding: utf-8 -*-

import math
import random

from animator import Image

class FadeToBlackAnimation(object):
    def __init__(self, duration = 3.0):
        self._duration = duration

    def animate(self, animator, img, draw):
        try:
            while animator.t < self._duration:
                # Fade screen
                faded = Image.eval(img, lambda x : x * 0.9)
                img.paste(faded)

                yield
        finally:
            animator.queue(self)