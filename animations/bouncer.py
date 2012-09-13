# -*- coding: utf-8 -*-

import math
import random

class Bot(object):
    def __init__(self, size, t0):
        self._size = size
        self.reset()

    def reset(self):
        self.direction = random.uniform(0, math.pi / 2.0)
        self.velocity = random.uniform(0.5, 1)
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
        self.x += self.v[0]
        if self.x < 0:
            self.x = -self.x
            self.v[0] = -self.v[0]
        if self.x > self._size[0]:
            self.x = 2 * self._size[0] - self.x
            self.v[0] = -self.v[0]

        self.y += self.v[1]
        if self.y < 0:
            self.y = -self.y
            self.v[1] = -self.v[1]
        if self.y > self._size[1]:
            self.y = 2 * self._size[1] - self.y
            self.v[1] = -self.v[1]

        return (self.x, self.y)


class BouncerAnimation(object):
    def __init__(self, bots=10):
        self._bots = bots

    def animate(self, animator, img, draw):
        size = img.size

        bots = [
            Bot(size, animator.t)
            for b in range(self._bots)
        ]

        try:
            while True:
                # Fade screen
                animator.fade(0.7)

                # Draw the bots
                pos = [bot.pos(animator.t) for bot in bots]
                draw.point(pos, fill="#ffffff")

                yield
        finally:
            animator.queue(self)