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
import traceback
from collections import deque

from twitter import Twitter, TwitterStream, OAuth, UserPassAuth

from animator import Image, ImageDraw, ImageFont
from colors import RAINBOW, RAINBOW_RGB

class TweetAnimation(object):
    def __init__(self, twitter_auth, track, fps, wait, speed, font, size, baseline):
        self._fetcher = TweetFetcher(self, twitter_auth, track)
        self._fps = fps
        self._wait = wait
        self._speed = speed
        self._font = ImageFont.truetype(font, size)
        self._baseline = baseline

        self._tweet_queue = deque(maxlen=128)
        self._image_queue = deque(maxlen=128)

        self._fetcher.start()

    def queue_tweet(self, tweet):
        # The deque is bounded, so new tweets will erase old ones
        # if the display cannot keep up.
        self._tweet_queue.append(tweet)

    def _generate_tweet_image(self, tweet):
        try:
            # Get strings from tweet
            author = '@' + tweet['user']['screen_name']
            text = tweet['text']
        except KeyError:
            # Malformed tweet (e.g. tweet deletion)
            return None

        # Compute text metrics
        author_size = self._font.getsize(author)
        text_size = self._font.getsize(text)

        # Compute image metrics
        img_size = (
            author_size[0] + 8 + text_size[0],
            max(author_size[1], text_size[1]) - self._baseline
        )

        # Create image
        img = Image.new("RGB", img_size)
        draw = ImageDraw.Draw(img)

        # Draw tweet in image
        author_color = RAINBOW[random.randint(0,len(RAINBOW)-1)]
        text_color = RAINBOW[random.randint(0,len(RAINBOW)-1)]
        draw.text((0, -self._baseline), author, font=self._font, fill=author_color)
        draw.text((author_size[0] + 4, -self._baseline), text, font=self._font, fill=text_color)
        draw.line(((img_size[0]-3,0),(img_size[0]-3,img_size[1]-1)), fill="#ffffff")

        # Keep the text as an attribute to the image
        # This helps with debugging
        img.text = author + ' ' + text

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

                # builds the tweet image
                img = self._generate_tweet_image(tweet)

                # img can be None if there are problem
                # drawing it
                if img is not None:
                    # Enqueue
                    self._image_queue.append(img)

                    # return the tweet image in the iterator
                    yield img
            except IndexError:
                break

    def animate(self, animator, img, draw):
        size = img.size

        # Origin of first line of text
        ox = 0

        # (x,y) is the drawing point for the next image
        x = ox
        y = 0

        # No need to scroll at first
        scroll = False

        while True:
            # Scroll the screen when the
            # last tweet ended up off screen.
            if scroll:
                ox = ox - self._speed
                scroll = False

            # Begin drawing at origin on first line
            x = ox
            y = 0

            # The iterator built by self._images() takes care
            # of the image queue, generating new images from tweets
            # as needed.
            image_iterator = self._images()

            # pop will tell us how many image we must remove
            # from left
            pop = 0

            try:
                start = time.time()

                # Get first image
                timg = image_iterator.next()

                while True:
                    # We drop images that are off the first line entirely
                    if x + timg.size[0] <= 0 and y == 0:
                        # Mark this image for later drop
                        # (iterator on deque doesn't support concurrent modifications)
                        pop = pop + 1

                        # Move drawing point AND origin accordingly
                        x = x + timg.size[0]
                        ox = ox + timg.size[0]

                        # Retry with next image
                        timg = image_iterator.next()
                        continue

                    # Paste the current image
                    img.paste(timg, (x, y))

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
                            scroll = True
                            break

            except StopIteration:
                pass

            # Sleep a bit
            # Note that if this FPS setting is bigger than for the animator,
            # the animator will win.
            if self._fps > 0:
                wait = (1.0 / self._fps) - (time.time() - start)
                if wait > 0:
                    time.sleep(wait)

            # Send image
            yield True

            # Pop tweets that are no longer needed
            if pop > 0:
                for i in range(pop):
                    self._image_queue.popleft()

                # Wait for 2 seconds once at least an image has been popped
                yield self._wait

class TweetFetcher(object):
    def __init__(self, animation, twitter_auth, track):
        self._animation = animation
        self._twitter_auth = twitter_auth
        self._track = track

    def start(self):
        # Launch Twitter stream fetcher
        self._thread = threading.Thread(name = "TweetFetcher", target = self._run)
        self._thread.daemon = True
        self._thread.start()

    def _run(self):
        try:
            twitter_stream = TwitterStream(auth = self._twitter_auth)

            # Display what is going to be tracked
            self._animation.queue_tweet(dict(
                user = dict(
                    screen_name = 'this_display'
                ),
                text = "tracking \"%s\""%self._track
            ))

            for tweet in twitter_stream.statuses.filter(track = self._track):
                self._animation.queue_tweet(tweet)
        except Exception, e:
            print "Could not connect to Twitter, generating random tweets"
            print "\t%s"%e

            for tweet in self._random():
                self._animation.queue_tweet(tweet)

    def _random(self):
        id_chars = u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        text_chars = id_chars + u"àéèïîôöùüç€$£              "

        def random_string(source, max_length):
            length = random.randint(1, max_length)
            result = []
            for i in range(length):
                result.append(random.choice(source))
            return "".join(result)

        while True:
            tweet = dict(
                user = dict(
                    screen_name = random_string(id_chars, 12)
                ),
                text = random_string(text_chars, 160)
            )
            yield tweet
            time.sleep(random.uniform(0,1))

