# -*- coding: utf-8 -*-

import serial
import time 

try:
    # in case of easy_installed PIL
    import Image, ImageDraw, ImageFont
except ImportError:
    # in case of distribution or windows PIL
    from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("Minecraftia.ttf", 8)
# font = ImageFont.truetype("uni05_53.ttf", 8)

def wave(t, mod):
    return abs(t%(mod*2-2)-mod+1)+1

class Display(object):
    def __init__(self, port='COM6:', baudrate=2000000):
        self._serial = serial.Serial(port, baudrate, timeout=1)

    def send_image(self, img):
        data = [2, 1] + [(value==2 and 3 or value) for pixel in img.getdata() for value in pixel]
        data = map(chr, data)
        data = "".join(data)
        self._serial.write(data)

class TweetAnimation(object):
    def __init__(self, tweet):
        self._tweet = tweet
        self._author = tweet['author']
        self._author_size = font.getsize(self._author)
        self._text = tweet['text']
        self._text_size = font.getsize(self._text)

    def draw(self, t):
        img = Image.new("RGB", (32, 16))
        draw = ImageDraw.Draw(img)

        # Draw the author name
        draw.text((-wave(t,self._author_size[0]-32), -3), self._author, font=font, fill="#660002")

        # Variable color for the text
        color_r = "%02x" % (100 + wave(t,155))
        color_g = "%02x" % wave(t,50)
        color_b = "%02x" % (wave(t,100) + wave(t-32,155))
        color = "#%s%s%s"%(color_r, color_g, color_b)
        draw.text((-wave(t,self._text_size[0]-32), 5), self._text, font=font, fill=color)
        
        return img

if __name__ == '__main__':
    tweet = dict(
        author = u'@nlehuen',
        text = u"Voix ambigüe d'un coeur qui au zéphyr préfère les jattes de kiwis. 1234567890"
    )

    display = Display()
    animation = TweetAnimation(tweet)

    t = 0
    while True:
        t = t + 1
        img = animation.draw(t)    
        display.send_image(img)
        time.sleep(0.05)