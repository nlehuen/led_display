# -*- coding: utf-8 -*-

import time
import traceback
import json

import animator

# Animations
import animations.tweet
import animations.rainbow
import animations.radar
import animations.fadetoblack
import animations.bouncer
import animations.heartbeat

import animations

if __name__ == '__main__':
    # Configuration file
    with open('configuration.json') as configuration_file:
        configuration = json.load(configuration_file)

    # Create display and animator

    display = None
    try:
        import leddisplay
        display = leddisplay.Display(
            port = configuration[u'leddisplay'][u'port'].encode(),
            speed = configuration[u'leddisplay'][u'speed']
        )
    except:
        traceback.print_exc()

    if display is None:
        import tkdisplay
        display = tkdisplay.Display((32, 16), 8)

    animator = animator.Animator(
        display,
        queue=configuration[u'animator'][u'queue'],
        fps=configuration[u'animator'][u'fps'],
        animation_timeout=configuration[u'animator'][u'timeout']
    )

    # Animation queue
    animator.queue(animations.heartbeat.HeartBeatAnimation())

    animator.queue(animations.fadetoblack.FadeToBlackAnimation(2))

    animator.queue(animations.bouncer.BouncerAnimation())

    animator.queue(animations.radar.RadarAnimation(bots=3, rps = 5))

    animator.queue(animations.fadetoblack.FadeToBlackAnimation(2))

    animator.queue(animations.rainbow.RainbowWoooowAnimation())

    animator.queue(animations.fadetoblack.FadeToBlackAnimation(2))

    # Launch tweet fetcher
    tweet_fetcher = animations.tweet.TweetFetcher(
        animator,
        animations.tweet.UserPassAuth(configuration['twitter']['login'], configuration['twitter']['password']),
        "#LED"
    )

    # For the moment, nothing more to do in the main thread
    animator.join()