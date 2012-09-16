# -*- coding: utf-8 -*-

import math
import random

from colors import RAINBOW

class HeartBeatAnimation(object):
    def __init__(self, duration):
        self._duration = duration

    def animate(self, animator, img, draw):
        size = img.size

        hb = random.randint(0,size[1]-1)

        while True:
            # Generate heart beat
            heartbeat = [hb]
            for i in range(1, size[0]):
                delta = random.uniform(0, 2) - 1.0
                hb = hb + delta
                if hb < 0 or hb >= size[1]:
                    hb = hb - 2 * delta
                heartbeat.append(hb)

            # Draw heartbeat
            for i, hb in enumerate(heartbeat):
                # Get out if timeout reached
                if self._duration > 0 and animator.t >= self._duration:
                    return

                # Fade screen
                animator.fade(0.95)

                # Draw the point
                draw.point((i, hb), fill=RAINBOW[int(hb * len(RAINBOW) / size[1])])

                yield

def build_animation(configuration):
    return HeartBeatAnimation(
        duration = configuration.duration.value(0)
    )