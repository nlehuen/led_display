# -*- coding: utf-8 -*-

import serial
import time
import threading
import traceback

# Ideas :
# Stream twitter feed / hashtag
# Display train / subway next departures
# Jenkins build status
# Number of subscribers to a service
# A nice RAINBOW Gradient Wooooooow
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
            return (
                int(c1[0] * i_f + c2[0] * f),
                int(c1[1] * i_f + c2[1] * f),
                int(c1[2] * i_f + c2[2] * f)
            )

    return [rainbow_color(i,512) for i in range(512)]

RAINBOW_RGB = build_rainbow()
RAINBOW = map(lambda c : "#%02x%02x%02x"%c, RAINBOW_RGB)

def wave(t, mod):
    return abs(t%(mod*2-2)-mod+1)+1

class Display(object):
    def __init__(self, port='COM6:', baudrate=2000000):
        try:
            self._serial = serial.Serial(port, baudrate, timeout=1)
        except:
            traceback.print_exc()
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
        self._animation = None
        self._animation_generator = None
        self._fps = fps
        self._wait = 1.0 / fps

    def queue(self, animation):
        return self._queue.put(animation, True, None)

    def _run(self):
        img = Image.new("RGB", (32, 16))
        draw = ImageDraw.Draw(img)

        # Timestamp of the last frame sent to the display
        # Initially it means nothing
        last_frame = time.time()

        self.start_time = None
        self.i = None
        while True:
            if self._animation is None:
                # Get next animation
                self._animation = self._queue.get(True, None)

                # Start frame generator, protecting the animator against exceptions
                try:
                    self._animation_generator = self._animation.animate(self, img, draw)
                except:
                    traceback.print_exc()
                    self._animation = None
                    self._animation_generator = None
                    continue

                # Record animation start
                self.start_time = time.time()
                self.i = 0

            # Update the animation time
            self.now = time.time()
            self.t = self.now - self.start_time

            # If there are other animations in the queue, kill this one once it
            # has been displayed for 15 seconds ; otherwise the animation will keep running
            # until it tells the Animator that it is over.
            keep_going = self._queue.empty() or self.t<=15.0

            if keep_going:
                try:
                    # Have the animation generate the next frame
                    self._animation_generator.next()

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

                    # Increment frame count
                    self.i = self.i + 1
                except StopIteration:
                    pass
                except:
                    traceback.print_exc()
            else:
                try:
                    # Close the generator, this sends a GeneratorExit
                    # into the animate() method.
                    self._animation_generator.close()
                except:
                    traceback.print_exc()
                self._animation = None
                self._animation_generator = None

class TweetAnimation(object):
    def __init__(self, tweet):
        self._tweet = tweet
        self._author_size = font.getsize(self._tweet['author'])
        self._text_size = font.getsize(self._tweet['text'])

    def animate(self, animator, img, draw):
        print "Starting", self._tweet['text']

        try:
            while True:
                # Clear the screen
                draw.rectangle([(0,0), img.size], fill="#000000")

                # Draw the author name
                color = RAINBOW[(animator.i*3 + 77) % len(RAINBOW)]
                pos = -wave(animator.i, self._author_size[0] - 32)
                draw.text((pos, -2), self._tweet['author'], font=font, fill=color)

                # Draw the text
                color = RAINBOW[animator.i % len(RAINBOW)]
                pos = -wave(animator.i, self._text_size[0] - 32)
                draw.text((pos, 5), self._tweet['text'], font=font, fill=color)

                # Send frame
                yield
        finally:
            print "KTHXBY", self._tweet['text']
            animator.queue(self)

class RainbowWoooowAnimation(object):
    def animate(self, animator, img, draw):
        size = img.size

        try:
            while True:
                for x in range(size[0]):
                    for y in range(size[1]):
                        idx = int(x * y + animator.i * 7)
                        draw.point((x, y), fill=RAINBOW[idx%len(RAINBOW)])
                yield
        finally:
            animator.queue(self)

if __name__ == '__main__':
    # Create display and animator
    display = Display()
    animator = Animator(display, 30)

    # Start animation in another thread
    animator_thread = threading.Thread(name = "Animator", target = animator._run)
    animator_thread.daemon = True
    animator_thread.start()

    animator.queue(RainbowWoooowAnimation())
    animator.queue(TweetAnimation(dict(
        author='@nlehuen',
        text="Voix ambigüe d'un coeur qui au zéphyr préfère les jattes de kiwis. 1234567890"
    )))

    # For the moment, nothing more to do in the main thread
    t = 0
    while True:
        t = t + 1
        time.sleep(1)