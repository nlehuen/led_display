# -*- coding: utf-8 -*-

import math
import random

class FadeToBlackAnimation(object):
    def __init__(self, duration, factor):
        self._duration = duration
        self._factor = factor

    def animate(self, animator, img, draw):
        while self._duration == 0 or animator.t < self._duration:
            # Fade screen
            animator.fade(self._factor)

            yield

def build_animation(configuration):
    return FadeToBlackAnimation(
        duration = configuration.duration.value(3),
        factor = configuration.factor.value(0.9)
    )