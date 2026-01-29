from waveshare_epd_4in2b import EPD_4in2_B


class PinkyDisplay:
    def __init__(self):
        self._epd = EPD_4in2_B()

    def clear(self):
        self._epd.imageblack.fill(0xFF)
        self._epd.imagered.fill(0x00)

    def text_black(self, text, x, y):
        self._epd.imageblack.text(text, x, y, 0x00)

    def text_red(self, text, x, y):
        self._epd.imagered.text(text, x, y, 0xFF)

    def set_black_framebuffer_bytes(self, buf: bytes):
        if len(buf) != len(self._epd.buffer_black):
            raise ValueError("Unexpected framebuffer size")
        self._epd.buffer_black[:] = buf
        self._epd.buffer_red[:] = b"\x00" * len(self._epd.buffer_red)

    def show(self):
        self._epd.EPD_4IN2B_Display(self._epd.buffer_black, self._epd.buffer_red)

    def sleep(self):
        self._epd.Sleep()
