import utime

import config
from pinky_display import PinkyDisplay


def main():
    display = PinkyDisplay()
    display.clear()

    colors = int(getattr(config, "DISPLAY_COLORS", 2))

    display.text_black("Hello World", 5, 10)

    label = "{} colours".format(colors)
    if colors == 3:
        display.text_red(label, 5, 40)
    else:
        display.text_black(label, 5, 40)

    display.show()
    utime.sleep_ms(20000)
    display.sleep()


main()
