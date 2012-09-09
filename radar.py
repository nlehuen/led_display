# -*- coding: utf-8 -*-

import math

from animator import Image, RAINBOW

class RadarAnimation(object):
    def __init__(self, rps = 4.0):
        self._rps = rps

    def animate(self, animator, img, draw):
        center = (img.size[0] / 2, img.size[1] / 2)
        radius = math.sqrt(center[0]**2 + center[1]**2)

        try:
            while True:
                # Fade screen
                faded = img.point(lambda x : x * 0.9)
                img.paste(faded)

                # One full rotation in self._rps seconds
                angle = 2 * math.pi * animator.t / self._rps

                to = (
                    center[0] + radius * math.cos(angle),
                    center[1] + radius * math.sin(angle)
                )

                draw.line((center, to), fill=RAINBOW[animator.i % len(RAINBOW)])

                yield
        finally:
            animator.queue(self)