# -*- coding: utf-8 -*-

import time
import traceback

import leddisplay
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
    # Create display and animator

    display = None
    try:
        display = leddisplay.Display()
    except:
        traceback.print_exc()

    if display is None:
        import tkdisplay
        display = tkdisplay.Display((32, 16))

    animator = animator.Animator(display, queue=256, fps=25, animation_timeout=30)

    # Animation queue
    #animator.queue(animations.heartbeat.HeartBeatAnimation())

    #animator.queue(animations.tweet.TweetAnimation(dict(
    #    author='@nlehuen',
    #    text=u"Voix ambigüe d'un coeur qui au zéphyr préfère les jattes de kiwis. 1234567890"
    #)))

    #animator.queue(animations.fadetoblack.FadeToBlackAnimation(2))

    #animator.queue(animations.bouncer.BouncerAnimation())

    #animator.queue(animations.radar.RadarAnimation(bots=3, rps = 5))

    #animator.queue(animations.fadetoblack.FadeToBlackAnimation(2))

    #animator.queue(animations.rainbow.RainbowWoooowAnimation())

    #animator.queue(animations.fadetoblack.FadeToBlackAnimation(2))

    # Launch tweet fetcher
    tweet_fetcher = animations.tweet.TweetFetcher(
        animator,
        animations.tweet.UserPassAuth('XXXXXX', 'XXXXXX')
    )

    # For the moment, nothing more to do in the main thread
    animator.join()