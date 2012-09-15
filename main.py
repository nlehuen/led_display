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
        twitter_auth = None

        # First, try to use the basic authentication
        auth_config = configuration.twitter.auth.basic
        if auth_config.exists():
            twitter_auth = animations.tweet.UserPassAuth(
                auth_config.login.required(),
                auth_config.password.required()
            )

        # If basic authentication was not found, try OAuth
        if twitter_auth is None:
            auth_config = configuration.twitter.auth.oauth
            if auth_config.exists():
                twitter_auth = animations.tweet.OAuth(
                    auth_config.oauth_token.required(),
                    auth_config.oauth_secret.required(),
                    auth_config.consumer_key.required(),
                    auth_config.consumer_secret.required(),
                )

        if twitter_auth is not None:
            animator.queue(animations.tweet.TweetAnimation(
                twitter_auth = twitter_auth,
                track = configuration.twitter.track.value(),
                fps = configuration.twitter.fps.value(0),
                wait = configuration.twitter.wait.value(1),
                speed = configuration.twitter.speed.value(1),
                font = configuration.twitter.font.value('alterebro-pixel-font.ttf'),
                size = configuration.twitter.size.value(16),
                baseline = configuration.twitter.baseline.value(4)
            ))
        else:
            print "You need to provide either twitter.auth.basic or"
            print "twitter.auth.oauth authentication informations."

    # For the moment, run the animator in the main thread
    animator.mainloop()