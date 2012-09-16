# -*- coding: utf-8 -*-

import time
import traceback
import json

from configuration import Configuration
import animator

# Animations
import animations.rainbow
import animations.radar
import animations.fadetoblack
import animations.bouncer
import animations.heartbeat

# Try to load Twitter animations
try:
    import animations.tweet
except ImportError:
    print "Please install twitter module from http://pypi.python.org/pypi/twitter/"
    animations.tweet = None

if __name__ == '__main__':
    # Load configuration
    configuration = Configuration.load('configuration.json')

    # Create display and animator

    display = None
    try:
        import leddisplay
        display = leddisplay.Display(
            port = configuration.leddisplay.port.required().encode(),
            speed = configuration.leddisplay.speed.required(),
            threaded = True
        )
    except leddisplay.serial.SerialException, e:
        print "Could not connect to serial port, launching display emulator"
        print "\t%s"%e
    except:
        traceback.print_exc()

    if display is None:
        import tkdisplay
        display = tkdisplay.Display(
            (
                configuration.tkdisplay.width.value(32),
                configuration.tkdisplay.height.value(16)
            ),
            configuration.tkdisplay.scale.value(4)
        )

    animator = animator.Animator(
        display,
        queue=configuration.animator.queue.value(120),
        fps=configuration.animator.fps.value(25),
        animation_timeout=configuration.animator.timeout.value(30)
    )

    # Animation queue
    if animations.tweet is not None:
        animator.queue(animations.tweet.TweetAnimation(configuration.twitter))

    # For the moment, run the animator in the main thread
    try:
        animator.mainloop()
    finally:
        display.close()