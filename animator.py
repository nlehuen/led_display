# -*- coding: utf-8 -*-

import threading
import time
import traceback
from Queue import Queue

try:
    # in case of easy_installed PIL
    import Image, ImageDraw, ImageFont
except ImportError:
    # in case of distribution or windows PIL
    from PIL import Image, ImageDraw, ImageFont

class Animator(object):
    def __init__(self, display, queue=0, fps=20, animation_timeout=15.0):
        self._display = display
        self._queue = Queue(queue)
        self._animation = None
        self._animation_generator = None
        self._fps = fps
        self._wait = 1.0 / fps
        self._animation_timeout = animation_timeout

        # Prepare image and draw surface
        self._img = Image.new("RGB", self._display.size())
        self._draw = ImageDraw.Draw(self._img)

        # Set public variables
        self.last_frame = time.time()
        self.start_time = None
        self.i = None

    def start(self):
        # Start animation in another thread
        self._thread = threading.Thread(name = "Animator", target = self.mainloop)
        self._thread.daemon = True
        self._thread.start()

    def join(self):
        "Wait for the animator to end."
        self._thread.join()

    def queue(self, animation, block=True, timeout=0):
        "Enqueue an animation. block and timeout have the same meaning as in the Queue.Queue.put method."
        return self._queue.put(animation, block, timeout)

    def wave(self, period):
        "Return a triangular wave signal from 0 to period-1"
        return abs(self.i%(period*2-2)-period+1)

    def fade(self, factor = 0.9):
        "Fade the display to black by the given factor"
        faded = Image.eval(self._img, lambda x : x * factor)
        self._img.paste(faded)

    def mainloop(self):
        "Main loop"
        keep_going = True
        while keep_going:
            keep_going = self.tick()

    def tick(self):
        "One animation step"
        if self._animation is None:
            # Get next animation
            self._animation = self._queue.get(True, None)

            # Start frame generator, protecting the animator against exceptions
            try:
                self._animation_generator = self._animation.animate(self, self._img, self._draw)
            except:
                traceback.print_exc()
                self._animation = None
                self._animation_generator = None
                return True

            # Record animation start
            self.start_time = time.time()
            self.i = 0

        # Update the animation time
        self.now = time.time()
        self.t = self.now - self.start_time

        # If there are other animations in the queue, kill this one once it
        # has been displayed for 15 seconds ; otherwise the animation will keep running
        # until it tells the Animator that it is over.
        keep_going = self._queue.empty() or self.t <= self._animation_timeout

        if keep_going:
            try:
                # Have the animation generate the next frame
                yielded = self._animation_generator.next()

                # Adjust wait time to maintain fixed frame rate
                # This assumes that sending the image to the display
                # is done at a fixed rate
                now = time.time()
                wait = self._wait - (now - self.last_frame)

                # If the animation yielded a number,
                # it's a number of seconds to wait on this frame.
                # Here we use a trick in order to skip using isinstance(send, numbers.Number)
                if yielded is not True:
                    # max(None, x) == x
                    # max(False, x) == x if x != 0
                    # max(True, x) == True
                    wait = max(yielded, wait)

                if wait > 0:
                    time.sleep(wait)
                    self.last_frame = time.time()
                else:
                    self.last_frame = now

                # Display next animation frame
                try:
                    if yielded is None or yielded is True:
                        self._display.send_image(self._img)
                except:
                    # If the display is broken, stop
                    # the animator
                    traceback.print_exc()
                    return False

                # Increment frame count
                self.i = self.i + 1
            except StopIteration:
                self._animation = None
                self._animation_generator = None
            except:
                traceback.print_exc()
                self._animation = None
                self._animation_generator = None
        else:
            try:
                # Close the generator, this sends a GeneratorExit
                # into the animate() method.
                self._animation_generator.close()
            except:
                traceback.print_exc()
            self._animation = None
            self._animation_generator = None

        return True