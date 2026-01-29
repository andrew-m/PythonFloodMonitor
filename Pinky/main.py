import utime

import config
from pinky_display import PinkyDisplay


def _load_framebuffer_bytes() -> bytes:
    source = str(getattr(config, "FRAMEBUFFER_SOURCE", "local")).strip().lower()

    if source == "local":
        filename = str(getattr(config, "LOCAL_FRAMEBUFFER_FILENAME", "")).strip()
        if not filename:
            raise ValueError("LOCAL_FRAMEBUFFER_FILENAME is not set")
        with open(filename, "rb") as f:
            return f.read()

    if source == "wifi":
        raise NotImplementedError("wifi framebuffer source not implemented yet")

    raise ValueError("Unknown FRAMEBUFFER_SOURCE")


def main():
    display = PinkyDisplay()
    display.clear()

    try:
        buf = _load_framebuffer_bytes()
        display.set_black_framebuffer_bytes(buf)
        display.show()
        utime.sleep_ms(20000)
        display.sleep()
        return
    except Exception:
        utime.sleep_ms(20000)
        display.sleep()


main()
