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
    "leddisplay":{
        "port":"/dev/ttyUSB0",
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

Development and debugging
-------------------------

If the serial port or display cannot be found, the `main.py` script emulates a display with a GUI window (using `Tkinter`). This means that you should be able to write and run animations without a LED display. It's less fun but it is much more practical when writing code on the go.

![Emulator screenshot](https://bitbucket.org/nlehuen/led_display/raw/488c7223873d/emulator-screenshot.png)

Changing animations
-------------------

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
