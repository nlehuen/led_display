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
import json

from twitter import Twitter, TwitterStream, OAuth, UserPassAuth

from animator import Image, ImageDraw, ImageFont
from colors import RAINBOW, RAINBOW_RGB

class TweetAnimation(object):
    def __init__(self, configuration):
        # First, try to use the basic authentication
        auth_config = configuration.auth.basic
        if auth_config.exists():
            basic_auth = UserPassAuth(
                auth_config.login.required(),
                auth_config.password.required()
            )
        else:
            basic_auth = None

        auth_config = configuration.auth.oauth
        if auth_config.exists():
            oauth = OAuth(
                auth_config.oauth_token.required(),
                auth_config.oauth_secret.required(),
                auth_config.consumer_key.required(),
                auth_config.consumer_secret.required(),
            )
        else:
            oauth = None

        self._fetcher = TweetFetcher(
            self,
            basic_auth,
            oauth,
            configuration.track.required()
        )
        self._duration = configuration.duration.value(0)
        self._fps = configuration.fps.value(0)
        self._wait = configuration.wait.value(1)
        self._speed = configuration.speed.value(1)
        self._font = ImageFont.truetype(
            configuration.font.value('fonts/alterebro-pixel-font.ttf'),
            configuration.size.value(16)
        )
        self._baseline = configuration.baseline.value(4)

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
            author = '@' + (tweet.get('from_user') or tweet['user']['screen_name'])
            text = tweet['text']
        except KeyError:
            # Malformed tweet (e.g. tweet deletion)
            print "Bad format for tweet :"
            print json.dumps(tweet, indent=True)
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

        # No need to scroll at first
        scroll = False

        try:
            while self._duration == 0 or animator.t < self._duration:
                animator.fade()

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

                    # Scroll the screen when the
                    # last tweet ended up off screen.
                    if scroll:
                        # Make sure that the origin aligns the image on its boundary
                        # should the speed parameter make it go further
                        ox = max(ox - self._speed, -timg.size[0])
                        scroll = False

                    # Begin drawing at origin on first line
                    x = ox
                    y = 0

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
                            # Scroll if some part of the image was offscreen
                            if y + timg.size[1] > size[1]:
                                scroll = True

                            timg = image_iterator.next()
                        else:
                            # The current image does not fit on the screen,
                            # so wrap it up on the next line
                            x = - ( size[0] - (x - timg.size[0]))
                            y = y + timg.size[1]

                            # End drawing if all vertical spaced
                            # is used
                            if y > size[1]:
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
        finally:
            self._fetcher.stop()

def chain(i1, i2):
    # itertools.chain does not support the close() method

    _i1 = None
    _i2 = None

    try:

        if i1 is not None:
            _i1 = iter(i1)
            for v in _i1:
                yield v
            _i1 = None

        if i2 is not None:
            _i2 = iter(i2)
            for v in _i2:
                yield v
            _i2 = None

    except GeneratorExit:
        if _i1 is not None:
            _i1.close()
        if _i2 is not None:
            _i2.close()

class TweetFetcher(object):
    def __init__(self, animation, basic_auth, oauth, track):
        self._animation = animation
        self._basic_auth = basic_auth
        self._oauth = oauth
        self._track = track

    def start(self):
        # Launch Twitter stream fetcher
        self._thread = threading.Thread(name = "TweetFetcher", target = self._run)
        self._thread.daemon = True
        self._keepgoing = True
        self._thread.start()

    def stop(self):
        self._keepgoing = False

    def _run(self):
        iterator = None

        # Display what is going to be tracked
        self._animation.queue_tweet(dict(
            user = dict(
                screen_name = 'this_display'
            ),
            text = "tracking \"%s\""%self._track
        ))

        try:
            if self._oauth:
                twitter = Twitter(domain="search.twitter.com", auth = self._oauth)
                i1 = twitter.search(q = self._track)
                i1 = i1['results']
            else:
                i1 = None

            if self._basic_auth:
                twitter_stream = TwitterStream(auth = self._basic_auth)
                i2 = twitter_stream.statuses.filter(track = self._track)
            else:
                i2 = None

            iterator = chain(i1, i2)

        except Exception, e:
            print "Could not connect to Twitter, generating random tweets"
            print "\t%s"%e

            iterator = self._random()

        try:
            while self._keepgoing:
                self._animation.queue_tweet(iterator.next())
            iterator.close()
        except StopIteration:
            pass

    def _random(self):
        id_chars = u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        text_chars = id_chars + u"àéèïîôöùüç€$£              "

        def random_string(source, max_length):
            length = random.randint(1, max_length)
            result = []
            for i in range(length):
                result.append(random.choice(source))
            return "".join(result)

        while self._keepgoing:
            tweet = dict(
                user = dict(
                    screen_name = random_string(id_chars, 12)
                ),
                text = random_string(text_chars, 160)
            )
            yield tweet
            time.sleep(random.uniform(0,1))

def build_animation(configuration):
    return TweetAnimation(configuration)