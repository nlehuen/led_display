# -*- coding: utf-8 -*-

import math
import random

class FadeToBlackAnimation(object):
    def __init__(self, duration = 3.0):
        self._duration = duration

    def animate(self, animator, img, draw):
        try:
            while animator.t < self._duration:
                # Fade screen
                animator.fade(0.9)

                yield
        finally:
            animator.queue(self)