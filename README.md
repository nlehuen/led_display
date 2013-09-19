led_display
===========

This project runs a set of animations on a LED display like [the one produced by hackspark.fr](http://hackspark.fr/fr/afficheur-a-led-rvb-controle-en-usb-de-32cm-x-16cm.html).

Hat tip
-------

Thanks to @jon1012 from Hackspark, first for their great display, then for the [HackSpark.LedDisplay](https://bitbucket.org/jon1012/hackspark.leddisplay) project that gave me lots of insights on how to program it.

Configuring the application
---------------------------

Copy `configuration-sample.json` into `configuration.json`, and modify settings :

```json
{
    "tkdisplay":{
        "width":32,
        "height":16,
        "scale":8
    },
    "leddisplay":{
        "port":"/dev/ttyUSB0",
        "speed":2000000
    },
    "animator":{
        "queue":256,
        "fps":25,
        "loop":true,
        "animations": [
            {"module":"animations.rainbow", "duration":30.0},
            {
                "module": "animations.tweet",
                "duration": 30.0,
                "auth":{
                    "basic":{
                        "login":"XXXXXX",
                        "password":"YYYYYY"
                    },
                    "oauth":{
                        "consumer_key":"",
                        "consumer_secret":"",
                        "oauth_token":"",
                        "oauth_secret":""
                    }
                },
                "track":"whatever",
                "fps":0,
                "wait":2.5,
                "speed":1,
                "font":"fonts/alterebro-pixel-font.ttf",
                "size":16,
                "baseline":4
            },
            {"module":"animations.heartbeat", "duration":30.0}
        ]
    }
}
```

`leddisplay.port` is the path to the serial port used to reach the LED display.

Running under Windows
---------------------

Getting a serial port to the display through the USB requires the [FT232 driver](http://www.ftdichip.com/FTDrivers.htm), in their [VCP declination](http://www.ftdichip.com/Drivers/VCP.htm), that is that the driver turns the USB device into a Virtual COM Port.

Once the driver is installed, when you plug the screen into a USB port you should get a new COM port, for instance `COM6:`. You can then configure it inside the `configuration.json` file :

```json
{
    "leddisplay":{
        "port":"COM6:",
        "speed":2000000
    },
    "twitter":{
        "login":"XXXXXX",
        "password":"YYYYYY",
        "track":"whatever"
    },
    "animator":{
        "queue":256,
        "fps":25,
        "timeout":30
    }
}
```

Running the application
-----------------------

```sh
python main.py
```

Display emulator
----------------

If the serial port or display cannot be found, the `main.py` script emulates a display with a GUI window (using `Tkinter`). This means that you should be able to write and run animations without a LED display. It's less fun but it is much more practical when writing code on the go.

![Emulator screenshot](https://raw.github.com/nlehuen/led_display/master/screenshots/emulator.png)

Tracking Twitter
----------------

The code comes with a Twitter ticker animation. It uses the [Twitter streaming API](https://dev.twitter.com/docs/api/1.1/post/statuses/filter) to track tweets with a given set of keywords.

![Twitter ticker screenshot](https://raw.github.com/nlehuen/led_display/master/screenshots/twitter.png)

Have a look at the `twitter` section in `configuration-sample.json` for a sample configuration. The syntax for the `twitter.track` parameter in explained in the [Twitter API documentation](https://dev.twitter.com/docs/streaming-apis/parameters#track).

The Twitter ticker animation requires a TrueType font to render text. "Pixel" fonts are of course recommended. Three small freeware fonts downloaded from [dafont.com](http://www.dafont.com/bitmap.php) are provided. Unfortunately they are more suited to Western language tweets, and you often get cyrillic, arabic or asian tweets when tracking popular keywords. Unicode fonts solve this problem, you can read about them in the [Unicode Font Guide For Free/Libre Open Source Operating Systems](http://unifont.org/fontguide/).

Finding a font that is both Unicode-friendly and pixel-friendly is not easy ; the best candidate yet is [unifont](http://unifoundry.com/unifont.html) (warning, due to a bad configuration of this web site's Apache server, when downloading a .gz file you end up with the original, uncompressed file stored on disk, yet still named with the .gz suffix), unfortunately it requires a height of 16 pixels to be legible.

As font metrics are sometimes quite greedy in space, you can tweak the `twitter.baseline` parameter to remove some space from above the font baseline. Experiment freely.

Changing the sequence of animations
-----------------------------------

For the moment, the sequence of animations is hand-coded within the `main.py` script. You can change their order, add some or remove some by editing this script.

Writing new animations
----------------------

Have a look at the various animations in the `animations` directory. Writing an animation is quite simple : you write a class that implements the `animate()` method. This method returns an iterator that is iterated once per frame.

A simple animation would be written like this :

```python
class StroboscopeAnimation(object):
    def animate(self, animator, img, draw):
        # animator.i => frame index
        # animator.t => frame timestamp (in seconds)
        # img => PIL Image instance which is edited by this animation
        # draw => PIL ImageDraw instance used to draw each frame

        while True:
            # On even frames, draw a white rectangle.
            # On odd frames, draw a black rectangle.
            # Net result : bleeding eyes (be careful !)
            if animator.i % 2 == 0:
                draw.rectangle([(0,0), img.size], fill="#000000")
            else:
                draw.rectangle([(0,0), img.size], fill="#ffffff")

            # Signal the animator that the frame has been drawn
            yield
```

When the animation yields, it tells the animator that it is done drawing, and that the frame can be sent to the display. If for any reason you want to skip a frame, you can do so by yielding `False` :

```python
class DoNothingAnimation(object):
    def animate(self, animator, img, draw):
        yield False
```

Yielding `False` allows the animator to skip sending the frame to the display, hence saving bandwidth etc. Of course you can also yield `True`, which is the same as yielding nothing.

The animation can also pause the animator by yielding the number of seconds (float) of the pause. See for example the `animations.tweet` module.
