# -*- coding: utf-8 -*-

# A nice RAINBOW Gradient Wooooooow

import math
import random

from colors import RAINBOW, RAINBOW_RGB

def rainbow1(animator, x, y):
    return RAINBOW_RGB[int(
        (x - 16) * 16 * math.sin(animator.t) + (y - 8) * 8 * math.sin(animator.t - 2) + animator.i * 7
    ) % len(RAINBOW_RGB)]

def rainbow2(animator, x, y):
    return RAINBOW_RGB[int(
        (x - 16) * (y - 8) + animator.i * 7
    ) % len(RAINBOW_RGB)]

def rainbow3(animator, x, y):
    return RAINBOW_RGB[int(
        8 * max(abs(x - 16), abs(y - 8)) + animator.i * 7
    ) % len(RAINBOW_RGB)]

rainbows = [
    rainbow1,
    rainbow2,
    rainbow3
]

class RainbowWoooowAnimation(object):
    def __init__(self, duration):
        self._duration = duration

    def animate(self, animator, img, draw):
        size = img.size

        last_t = -100
        while self._duration == 0 or animator.t < self._duration:
            # Change rainbow every 8 seconds
            if animator.t - last_t > 8:
                rainbow_function = random.choice(rainbows)
                last_t = animator.t

            # Example using Image.putdata instead of multiple
            # Image.putpixel or ImageDraw.point calls
            rainbow = [
                rainbow_function(animator, x, y)
                for y in range(size[1])
                for x in range(size[0])
            ]
            img.putdata(rainbow)

            # Send image
            yield

def build_animation(configuration):
    return RainbowWoooowAnimation(
        duration = configuration.duration.value(0)
    )