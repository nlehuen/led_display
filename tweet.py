# -*- coding: utf-8 -*-

import serial
import time 
import threading

# Ideas :
# Stream twitter feed / hashtag
# Display train / subway next departures
# Jenkins build status
# Number of subscribers to a service
# ...

try:
    # in case of easy_installed PIL
    import Image, ImageDraw, ImageFont
except ImportError:
    # in case of distribution or windows PIL
    from PIL import Image, ImageDraw, ImageFont

from Queue import Queue

font = ImageFont.truetype("Minecraftia.ttf", 8)
# font = ImageFont.truetype("Zepto 1.100.ttf", 8)

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

    return [rainbow_color(i,512) for i in range(512)]

RAINBOW = build_rainbow() 

def wave(t, mod):
    return abs(t%(mod*2-2)-mod+1)+1

class Display(object):
    def __init__(self, port='COM6:', baudrate=2000000):
        try:
            self._serial = serial.Serial(port, baudrate, timeout=1)
        except:
            self._serial = None
        self._matrix_command = [chr(2), chr(1)]

    def send_image(self, img):
        if img.size != (32, 16):
            img = img.crop((0, 0, 32, 16))
        data = self._matrix_command
        data = data + [(value==2 and chr(3) or chr(value)) for pixel in img.getdata() for value in pixel]
        data = "".join(data)
        if self._serial is not None:
            self._serial.write(data)

class Animator(object):
    def __init__(self, display, fps=20):
        self._display = display
        self._queue = Queue()
        self._current = None
        self._fps = fps
        self._wait = 1.0 / fps

    def queue(self, animation):
        return self._queue.put(animation, True, None)

    def run(self):
        img = Image.new("RGB", (32, 16))
        draw = ImageDraw.Draw(img)

        last_frame = time.time()
        start_time = None
        i = None
        while True:
            if self._current is None:
                # Get next animation
                self._current = self._queue.get(True, None)

                # Start animation
                self._current.start(self, img, draw)
                start_time = time.time()
                i = 0

            # Update the animation time
            t = time.time() - start_time

            # If there are other animations in the queue, kill this one once it
            # has been displayed for 15 seconds ; otherwise the animation will keep running
            # until it tells the Animator that it is over.
            keep_going = self._queue.empty() or t<15.0
            if keep_going and self._current.update(self, img, draw, t, i):
                # Adjust wait time to maintain fixed frame rate
                # This assumes that sending the image to the display
                # is done at a fixed rate
                now = time.time()
                wait = self._wait - (now - last_frame)
                if wait > 0:
                    time.sleep(wait)
                    last_frame = time.time()
                else:
                    last_frame = now

                # Display next animation frame
                self._display.send_image(img)

                # Next frame                
                i = i + 1
            else:
                # No more frame in the animation, time
                # to move to the next one
                # Ends animation
                self._current.stop(self, img, draw)
                self._current = None

class TweetAnimation(object):
    def __init__(self, tweet):
        self._tweet = tweet
        self._author_size = font.getsize(self._tweet['author'])
        self._text_size = font.getsize(self._tweet['text'])

    def start(self, animator, img, draw):
        print "Starting " + self._tweet['text']

    def stop(self, animator, img, draw):
        pass

    def update(self, animator, img, draw, t, i):
        # Clear the screen
        draw.rectangle([(0,0), img.size], fill="#000000")

        # Draw the author name
        color = RAINBOW[(i*3 + 77) % len(RAINBOW)]
        pos = -wave(i, self._author_size[0] - 32)
        draw.text((pos, -2), self._tweet['author'], font=font, fill=color)

        # Draw the text
        color = RAINBOW[i % len(RAINBOW)]
        pos = -wave(i, self._text_size[0] - 32)
        draw.text((pos, 5), self._tweet['text'], font=font, fill=color)
        
        return True

class TweetCollector(object):
    pass

if __name__ == '__main__':
    display = Display()
    animator = Animator(display, 10)

    # Start animation in another thread
    animator_thread = threading.Thread(name = "Animator", target = animator.run)
    animator_thread.daemon = True
    animator_thread.start()

    # Enqueue first animation
    animator.queue(TweetAnimation(dict(
        author = u'@nlehuen',
        text = u"Voix ambigüe d'un coeur qui au zéphyr préfère les jattes de kiwis. 1234567890"
    )))

    # Enqueue first animation
    animator.queue(TweetAnimation(dict(
        author = u'@nlehuen',
        text = u"This is another tweet"
    )))

    # For the moment, nothing more to do in the main thread
    t = 0
    while True:
        print t
        t = t + 1
        time.sleep(1)