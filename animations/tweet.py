# -*- coding: utf-8 -*-

# Ideas :
# Stream twitter feed / hashtag
# Display train / subway next departures
# Jenkins build status
# Number of subscribers to a service
# ...

import threading
import time

try:
    from twitter import Twitter, TwitterStream, OAuth, UserPassAuth
except:
    print "Please install twitter module from http://pypi.python.org/pypi/twitter/"


from animator import RAINBOW, RAINBOW_RGB, ImageFont

font = ImageFont.truetype("Minecraftia.ttf", 8)

class TweetAnimation(object):
    def __init__(self, tweet, duration=0, repeat=True):
        self._tweet = tweet
        self._duration = duration
        self._repeat = repeat
        self._t0 = time.time()

        self._author = '@' + self._tweet[u'user'][u'screen_name']
        self._text = self._tweet[u'text']

    def animate(self, animator, img, draw):
        size = img.size
        author_size = font.getsize(self._author)
        text_size = font.getsize(self._text)

        try:
            while self._duration==0 or animator.t < self._duration:
                # Clear the screen
                draw.rectangle([(0,0), img.size], fill="#000000")

                # Draw the author name
                color = RAINBOW[(animator.i*3 + 77) % len(RAINBOW)]
                pos = -animator.wave(author_size[0] - size[0] - 3)
                draw.text((pos, -3), self._author, font=font, fill=color)

                # Draw the text
                color = RAINBOW[animator.i % len(RAINBOW)]
                pos = -animator.wave(text_size[0] + size[0])
                draw.text((pos, 5), self._text, font=font, fill=color)

                # Send frame
                yield
        finally:
            # Put this animation back into the queue
            if self._repeat:
                animator.queue(self)

class TweetFetcher(object):
    def __init__(self, animator, twitter_auth, duration=5):
        self._animator = animator
        self._twitter_auth = twitter_auth
        self._duration = duration

        # Launch Twitter stream fetcher
        self._thread = threading.Thread(name = "Twitter", target = self._run)
        self._thread.daemon = True
        self._thread.start()

    def _run(self):
        twitter_stream = TwitterStream(auth = self._twitter_auth)

        for tweet in twitter_stream.statuses.sample():
            try:
                tweet_animation = TweetAnimation(tweet, duration=self._duration, repeat=False)
                self._animator.queue(tweet_animation, block=False)
            except:
                pass

