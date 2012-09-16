# -*- coding: utf-8 -*-

import time
import traceback
import json

from configuration import Configuration
import animator

import importlib

# Try to load Twitter animations
try:
    import animations.tweet
except ImportError:
    print "Please install twitter module from http://pypi.python.org/pypi/twitter/"
    animations.tweet = None

if __name__ == '__main__':
    # Load configuration
    configuration = Configuration.load('configuration.json')

    # Try to connect to LED display through serial port
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

    # If connection to LED display was not successfull,
    # launch the emulator
    if display is None:
        import tkdisplay
        display = tkdisplay.Display(
            (
                configuration.tkdisplay.width.value(32),
                configuration.tkdisplay.height.value(16)
            ),
            configuration.tkdisplay.scale.value(4)
        )

    # Create the animator
    animator = animator.Animator(
        display,
        configuration.animator
    )

    # For the moment, run the animator in the main thread
    try:
        animator.mainloop()
    finally:
        display.close()