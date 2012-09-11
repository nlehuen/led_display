# -*- coding: utf-8 -*-

import math
import random

from animator import Image, RAINBOW

class HeartBeatAnimation(object):
    def animate(self, animator, img, draw):
        size = img.size

        try:
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
                    # Fade screen
                    faded = Image.eval(img, lambda x : x * 0.95)
                    img.paste(faded)

                    # Draw the point
                    draw.point((i, hb), fill=RAINBOW[int(hb * len(RAINBOW) / size[1])])

                    yield
        finally:
            animator.queue(self)