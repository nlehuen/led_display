# -*- coding: utf-8 -*-

import math
import random

from animator import Image, RAINBOW

class Bot(object):
    def __init__(self, size, t0):
        self._size = size
        self.reset(t0)

    def reset(self, t0):
        self.t0 = t0
        self.direction = random.uniform(0, math.pi / 2.0)
        self.velocity = random.uniform(0.5, 5)
        self.v = [
            self.velocity * math.cos(self.direction),
            self.velocity * math.sin(self.direction)
        ]

        if random.randint(0,1):
            # Vertical side
            if random.randint(0, 1):
                # Right side
                self.x = self._size[0] - 1
                self.v[0] = -self.v[0]
            else:
                # Left side
                self.x = 0
            self.y = random.randint(0, self._size[1]-1)
        else:
            # Horizontal side
            self.x = random.randint(0, self._size[0]-1)
            if random.randint(0, 1):
                # Lower side
                self.y = self._size[1] - 1
                self.v[1] = -self.v[1]
            else:
                self.y = 0

    def pos(self, t):
        while True:
            x = self.x + self.v[0] * (t - self.t0)
            y = self.y + self.v[1] * (t - self.t0)

            if x < 0 or x > self._size[0] or y < 0 or y > self._size[1]:
                self.reset(t)
            else:
                return (x, y)

class RadarAnimation(object):
    def __init__(self, rps = 3.0):
        self._rps = rps

    def animate(self, animator, img, draw):
        size = img.size
        center = (size[0] / 2, size[1] / 2)
        radius = math.sqrt(center[0]**2 + center[1]**2)

        bots = [
            Bot(size, animator.t)
            for b in range(4)
        ]

        try:
            while True:
                # Fade screen
                faded = Image.eval(img, lambda x : x * 0.9)
                img.paste(faded)

                # Draw the radar line
                # One full rotation in self._rps seconds
                angle = 2 * math.pi * animator.t / self._rps
                to = (
                    center[0] + radius * math.cos(angle),
                    center[1] + radius * math.sin(angle)
                )
                draw.line((center, to), fill=RAINBOW[animator.i % len(RAINBOW)])

                # Draw the bots
                # TODO : only draw dots lying on the radar line
                draw.point([bot.pos(animator.t) for bot in bots], fill="#ffffff")

                yield
        finally:
            animator.queue(self)