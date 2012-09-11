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

font = ImageFont.truetype("alterebro-pixel-font.ttf", 16)

class TweetAnimation(object):
    def __init__(self, tweet):
        self._tweet = tweet
        self._t0 = time.time()

        self._author = '@' + self._tweet[u'user'][u'screen_name']
        self._text = self._tweet[u'text']

    def animate(self, animator, img, draw):
        size = img.size
        author_size = font.getsize(self._author)
        author_length = author_size[0] + size[0]
        text_size = font.getsize(self._text)
        text_length = text_size[0] + size[0]

        end_loop = max(
            author_length,
            text_length
        ) - 1

        while animator.i != end_loop:
            # Clear the screen
            draw.rectangle([(0,0), img.size], fill="#000000")

            # Draw the author name
            color = RAINBOW[(animator.i*3 + 77) % len(RAINBOW)]
            pos = size[0] - (animator.i % author_length)
            draw.text((pos, -4), self._author, font=font, fill=color)

            # Draw the text
            color = RAINBOW[animator.i % len(RAINBOW)]
            pos = size[0] - (animator.i % text_length)
            draw.text((pos, 4), self._text, font=font, fill=color)

            # Send frame
            yield


class TweetFetcher(object):
    def __init__(self, animator, twitter_auth, track):
        self._animator = animator
        self._twitter_auth = twitter_auth
        self._track = track

        # Launch Twitter stream fetcher
        self._thread = threading.Thread(name = "Twitter", target = self._run)
        self._thread.daemon = True
        self._thread.start()

    def _run(self):
        twitter_stream = TwitterStream(auth = self._twitter_auth)

        for tweet in twitter_stream.statuses.filter(track = self._track):
            try:
                tweet_animation = TweetAnimation(tweet)
                self._animator.queue(tweet_animation, block=False)
            except:
                pass

