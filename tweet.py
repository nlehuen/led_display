# -*- coding: utf-8 -*-

import serial
import time 

try:
    # in case of easy_installed PIL
    import Image, ImageDraw, ImageFont
except ImportError:
    # in case of distribution or windows PIL
    from PIL import Image, ImageDraw, ImageFont

from Queue import Queue

font = ImageFont.truetype("Minecraftia.ttf", 8)
# font = ImageFont.truetype("uni05_53.ttf", 8)

def build_rainbow():
    RAINBOW_COLORS = (
        (255, 0, 0),
        (255, 127, 0),
        (255, 255, 0),
        (0, 255, 0),
        (0, 0, 255),
        (111, 0, 255),
        (143, 0, 255),
        (255, 0, 0)
    )

    def rainbow_color(t, r):
        "Returns a rainbow color, 0 <= t <= r"
        if t == r:
            return RAINBOW_COLORS[-1]
        else:
            idx = 1.0 * (len(RAINBOW_COLORS) - 1) * t / r
            iidx = int(idx)
            f = idx - iidx
            i_f = 1.0 - f
            c1 = RAINBOW_COLORS[iidx]
            c2 = RAINBOW_COLORS[iidx + 1]
            return "#%02x%02x%02x"%(
                int(c1[0] * i_f + c2[0] * f),
                int(c1[1] * i_f + c2[1] * f),
                int(c1[2] * i_f + c2[2] * f)
            )
    return [rainbow_color(i,256) for i in range(256)]

RAINBOW = build_rainbow() 

def wave(t, mod):
    return abs(t%(mod*2-2)-mod+1)+1

class Display(object):
    def __init__(self, port='COM6:', baudrate=2000000):
        self._serial = serial.Serial(port, baudrate, timeout=1)
        self._matrix_command = [chr(2), chr(1)]

    def send_image(self, img):
        data = self._matrix_command + [(value==2 and chr(3) or chr(value)) for pixel in img.getdata() for value in pixel]
        data = "".join(data)
        self._serial.write(data)

class Animator(object):
    def __init__(self, display):
        self._display = display
        self._queue = Queue()
        self._current = None

    def queue(self, animation):
        return self._queue.put(animation, True, None)

    def run(self):
        img = Image.new("RGB", (32, 16))
        draw = ImageDraw.Draw(img)

        t = None
        while True:
            if self._current is None:
                self._current = self._queue.get(True, None)
                self._current.start(self, img, draw)
                t = 0

            if self._current.draw(self, img, draw, t):
                self._display.send_image(img)
                t = t + 1
                time.sleep(0.05)
            else:
                # Ends animation
                self._current.stop(self, img, draw)
                self._current = None

class TweetAnimation(object):
    def __init__(self, tweet):
        self._tweet = tweet
        self._author = tweet['author']
        self._author_size = font.getsize(self._author)
        self._text = tweet['text']
        self._text_size = font.getsize(self._text)

    def start(self, animator, img, draw):
        pass

    def stop(self, animator, img, draw):
        pass

    def draw(self, animator, img, draw, t):
        # Clear the screen
        draw.rectangle([(0,0), img.size], fill="#000000")

        # Draw the author name
        color = RAINBOW[(t + 77) % len(RAINBOW)]
        draw.text((-wave(t,self._author_size[0]-32), -3), self._author, font=font, fill=color)

        # Draw the text
        color = RAINBOW[t % len(RAINBOW)]
        draw.text((-wave(t,self._text_size[0]-32), 5), self._text, font=font, fill=color)
        
        return True

if __name__ == '__main__':
    tweet = dict(
        author = u'@nlehuen',
        text = u"Voix ambigüe d'un coeur qui au zéphyr préfère les jattes de kiwis. 1234567890"
    )

    display = Display()
    animator = Animator(display)

    animator.queue(TweetAnimation(tweet))

    animator.run()
