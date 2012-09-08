# -*- coding: utf-8 -*-

# Ideas :
# Stream twitter feed / hashtag
# Display train / subway next departures
# Jenkins build status
# Number of subscribers to a service
# ...

from animator import RAINBOW, RAINBOW_RGB, ImageFont

font = ImageFont.truetype("Minecraftia.ttf", 8)

class TweetAnimation(object):
    def __init__(self, tweet):
        self._tweet = tweet
        self._author_size = font.getsize(self._tweet['author'])
        self._text_size = font.getsize(self._tweet['text'])

    def animate(self, animator, img, draw):
        print "Starting", self._tweet['text']

        try:
            while True:
                # Clear the screen
                draw.rectangle([(0,0), img.size], fill="#000000")

                # Draw the author name
                color = RAINBOW[(animator.i*3 + 77) % len(RAINBOW)]
                pos = -animator.wave(self._author_size[0] - 32)
                draw.text((pos, -3), self._tweet['author'], font=font, fill=color)

                # Draw the text
                color = RAINBOW[animator.i % len(RAINBOW)]
                pos = -animator.wave(self._text_size[0] - 32)
                draw.text((pos, 5), self._tweet['text'], font=font, fill=color)

                # Send frame
                yield
        finally:
            print "KTHXBY", self._tweet['text']

            # Put this animation back into the queue
            animator.queue(self)

