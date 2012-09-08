# -*- coding: utf-8 -*-

import time
import traceback

import leddisplay
import animator
import tweet

if __name__ == '__main__':
    # Create display and animator

    display = None
    try:
        display = leddisplay.Display()
    except:
        traceback.print_exc()

    if display is None:
        import tkdisplay
        display = tkdisplay.Display()

    animator = animator.Animator(display, fps=30, animation_timeout=30)

    animator.queue(tweet.TweetAnimation(dict(
        author='@nlehuen',
        text=u"Voix ambigüe d'un coeur qui au zéphyr préfère les jattes de kiwis. 1234567890"
    )))
    animator.queue(tweet.RainbowWoooowAnimation())

    # For the moment, nothing more to do in the main thread
    animator.join()