# -*- coding: utf-8 -*-

import time
import traceback
import json

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
    # Configuration file
    with open('configuration.json') as configuration_file:
        configuration = json.load(configuration_file)

    # Create display and animator

    display = None
    try:
        import leddisplay
        display = leddisplay.Display(
            port = configuration['leddisplay']['port'].encode(),
            speed = configuration['leddisplay']['speed'],
            threaded = True
        )
    except:
        traceback.print_exc()

    if display is None:
        import tkdisplay
        display = tkdisplay.Display((32, 16), 8)

    animator = animator.Animator(
        display,
        queue=configuration['animator']['queue'],
        fps=configuration['animator']['fps'],
        animation_timeout=configuration['animator']['timeout']
    )

    # Animation queue
    animator.queue(animations.rainbow.RainbowWoooowAnimation())

    animator.queue(animations.heartbeat.HeartBeatAnimation())

    animator.queue(animations.bouncer.BouncerAnimation())

    animator.queue(animations.radar.RadarAnimation(bots=3, rps = 5))

    animator.queue(animations.fadetoblack.FadeToBlackAnimation(2))

    if animations.tweet is not None:
        animator.queue(animations.tweet.TweetAnimation(
            twitter_auth = animations.tweet.UserPassAuth(
                configuration['twitter']['login'],
                configuration['twitter']['password']
            ),
            track = configuration['twitter']['track'],
            speed = configuration['twitter'].get('speed', 1),
            wait = configuration['twitter'].get('wait', 1),
            font = configuration['twitter'].get('font', 'alterebro-pixel-font.ttf'),
            size = configuration['twitter'].get('size', 16),
            baseline = configuration['twitter'].get('baseline', 4)
        ))

    # For the moment, run the animator in the main thread
    animator.mainloop()