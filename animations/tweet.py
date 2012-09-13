# -*- coding: utf-8 -*-

# Ideas :
# Stream twitter feed / hashtag
# Display train / subway next departures
# Jenkins build status
# Number of subscribers to a service
# ...

import threading
import time
import random
from collections import deque

from twitter import Twitter, TwitterStream, OAuth, UserPassAuth

from animator import RAINBOW, RAINBOW_RGB, Image, ImageDraw, ImageFont

font = ImageFont.truetype("alterebro-pixel-font.ttf", 16)

class TweetAnimation(object):
    def __init__(self, twitter_auth, track, speed=1):
        self._fetcher = TweetFetcher(self, twitter_auth, track)
        self._speed = speed

        self._tweet_queue = deque(maxlen=128)
        self._image_queue = deque(maxlen=128)

        self._fetcher.start()

    def queue_tweet(self, tweet):
        self._tweet_queue.append(tweet)

    def _generate_tweet_image(self, tweet):
        # Get strings from tweet
        author = '@' + tweet['user']['screen_name']
        text = tweet['text'][:16]

        # Compute text metrics
        author_size = font.getsize(author)
        text_size = font.getsize(text)

        # Compute image metrics
        img_size = (
            author_size[0] + 8 + text_size[0],
            max(author_size[1], text_size[1])
        )

        # Create image
        img = Image.new("RGB", img_size)
        draw = ImageDraw.Draw(img)

        # Draw tweet in image
        author_color = RAINBOW[random.randint(0,len(RAINBOW)-1)]
        text_color = RAINBOW[random.randint(0,len(RAINBOW)-1)]
        draw.text((0, 0), author, font=font, fill=author_color)
        draw.text((author_size[0] + 4, 0), text, font=font, fill=author_color)
        draw.line(((img_size[0]-3,0),(img_size[0]-3,img_size[1]-1)), fill="#ffffff")

        return img

    def _images(self):
        # First, iterate images from the queue
        for img in self._image_queue:
            yield img

        # Once all images from the queue have been used,
        # and if the iterator is not yet closed, generate new images from
        # the tweet queue
        while True:
            try:
                # get a tweet from the tweet queue
                tweet = self._tweet_queue.popleft()
                # builds the tweet image and enqueue it
                img = self._generate_tweet_image(tweet)
                self._image_queue.append(img)
                # return the tweet image in the iterator
                yield img
            except IndexError:
                break

    def animate(self, animator, img, draw):
        size = img.size

        ox = 1
        while True:
            if animator.i % self._speed != 0:
                # We skip painting the screen
                yield

            ox = ox - 1
            x = ox
            y = 0

            # Iterate on all images. The iterator built
            # by self._images() takes care of the image queue,
            # generating new images as needed.
            pop = 0
            image_iterator = self._images()

            try:
                timg = image_iterator.next()
                while True:
                    # We drop images that are off the first line entirely
                    if x + timg.size[0] <= 0 and y == 0:
                        pop = pop + 1
                        x = x + timg.size[0]
                        ox = ox + timg.size[0]
                        continue

                    # Paste the current image
                    img.paste(timg, (x,y))

                    # Move the cursor
                    x = x + timg.size[0]

                    # If end of image reached within the screen,
                    # get the next image to paint
                    if x < size[0]:
                        timg = image_iterator.next()
                    else:
                        # The current image does not fit on the screen,
                        # so wrap it up on the next line
                        x = - ( size[0] - (x - timg.size[0]))
                        y = y + timg.size[1]

                        # End drawing if all vertical spaced
                        # is used
                        if y > img.size[1]:
                            break

            except StopIteration:
                pass

            # Pop images that are no longer needed
            if pop > 0:
                print "Removing image"
                for i in range(pop):
                    self._image_queue.popleft()

            # Send image
            yield

class TweetFetcher(object):
    def __init__(self, animation, twitter_auth, track):
        self._animation = animation
        self._twitter_auth = twitter_auth
        self._track = track

    def start(self):
        # Launch Twitter stream fetcher
        self._thread = threading.Thread(name = "Twitter", target = self._run)
        self._thread.daemon = True
        self._thread.start()

    def _run(self):
        twitter_stream = TwitterStream(auth = self._twitter_auth)

        for tweet in twitter_stream.statuses.filter(track = self._track):
            self._animation.queue_tweet(tweet)
