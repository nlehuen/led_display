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
    def __init__(self, bots=2, rps = 3.0):
        self._bots = bots
        self._rps = rps

    def animate(self, animator, img, draw):
        size = img.size
        center = (size[0] / 2, size[1] / 2)
        radius = math.sqrt(center[0]**2 + center[1]**2)

        bots = [
            Bot(size, animator.t)
            for b in range(self._bots)
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
                draw.line((center, to), fill="#009900")

                def visible(a, b, limit):
                    # Custom made visibility algo :
                    # Vector coordinates have the same sign
                    # and norm of vectorial product is less than a limit
                    # (which means both vectors are nearly colinear)
                    # Normally |u x v| = |u| . |v| . sin(angle(u, v))
                    # Therefore if the angle is small enough, |u x v| is small
                    u1 = a[0] - center[0]
                    u2 = b[0] - center[0]
                    v1 = a[1] - center[1]
                    v2 = b[1] - center[1]
                    mul = abs(u1 * v2 - u2 * v1) # |u x v| if u and v are on the same (X,Y) plane
                    return 0 <= u1*u2 and 0 <= v1*v2 and 0 <= mul and mul <= limit

                # Draw the bots
                pos = [bot.pos(animator.t) for bot in bots]
                pos = [bot for bot in pos if visible(bot, to, 25)]
                draw.point(pos, fill="#ffffff")

                yield
        finally:
            animator.queue(self)