# Pinky - (the Inly Pico Display)

Pinky is written in Micropython, runs on a Raspberry Pi Pico, and has an attached Waveshare 4.2" e-ink display. Either 2 colour (Black and White) or 3 colour (Black, Red and White).

## Walking Skeleton

* Step 1 is Hello world.
    We'll create a main python file and a config file. The config will show if it's a 2 colour or 3 colour e-ink display.

    Main will check the config, and then write a Hello World message in black. Then the number of colours the display has, in black if it's a two colour display, and in red if it's a three colour display (so there's some red and some black for the 3 colour display).

    E-ink driver code will be based on the Waveshare micropython example code. This code is kind of ugly, so as we go along will use encapsulation and abatraction to keep our code away from it. I don't care if the wave-share guff is in the main.py file or in a seperate fule, but I do want to keep it away from the rest of our code, by keeping our significant chunks of logic in seperate files.

    For now there is no need to connect to a network, fetch any data etc. Just displaying a static message. 

    Documentation for the e-ink display is here: https://www.waveshare.com/wiki/Pico-ePaper-4.2- B (look down for the "Micropython series")
    But easier to just adapt and copy the open source example. @WaveshareExampleCode/Pico-ePaper-4.2-B.py


## Notes / gotchas (display buffer semantics)

The Waveshare 4.2" B/W/Red driver transmits the red plane with an inversion (`~redImage[...]`) when sending bytes to the display.

This means the "obvious" framebuffer conventions are flipped for the red plane:
- Clearing the red buffer to `0xFF` will often produce a full red screen.
- To clear the display to no-red, the red framebuffer must be filled with `0x00`.
- To draw red pixels/text into the red framebuffer, use `0xFF` for the draw colour.

We fixed this in `pinky_display.py` by using:
- `imagered.fill(0x00)` in `clear()`
- `imagered.text(..., 0xFF)` in `text_red()`


## Step 2, load and display Fletcher's framebuffer data.

Pinky fetches the pre-rendered framebuffer data from Fletcher and displays it on the e-ink panel.

### Data source configuration

`config.py` includes:
- `FRAMEBUFFER_SOURCE` - either `"local"` or `"wifi"`
- `LOCAL_FRAMEBUFFER_FILENAME` - filename for local testing (e.g. `"example_bw.bin"`)
- `FLETCHER_LATEST_BIN_URL` - S3 URL for WiFi fetch

### Local mode
Loads the framebuffer bytes from a file on the Pico's filesystem. Useful for testing without network connectivity.

### WiFi mode
WiFi credentials are stored in `secrets.py` (gitignored):
- `WIFI_SSID` - network name
- `WIFI_PASSWORD` - network password

A template `secrets.py.example` is provided in the repo.

The `wifi_helper.py` module provides:
- `connect_wifi(ssid, password, timeout_s=30)` - connects using `network.WLAN(network.STA_IF)`
- `disconnect_wifi()` - disconnects and deactivates interface to save power

When `FRAMEBUFFER_SOURCE = "wifi"`, Pinky:
1. Connects to WiFi
2. Fetches `FLETCHER_LATEST_BIN_URL` using `urequests.get()`
3. Disconnects WiFi (power saving)
4. Loads the 15000 bytes into the black framebuffer
5. Displays the image

### Framebuffer format
Fletcher's `latest.bin` is exactly 15000 bytes (400×300÷8) in `MONO_HLSB` format, matching the Waveshare driver's black plane buffer. Pinky loads it directly via `set_black_framebuffer_bytes()` with no decoding needed.

## Step 3, startup debug display.

Bearing in mind the Waveshare display takes more than 15 seconds to update, it would still be useful to display some debugging information on startup.

When `main.py` runs, it:
1. Collects debug messages during config loading, WiFi connection, and data fetch
2. Displays all debug messages as simple text on screen (using framebuffer's built-in `text()` method)
3. Waits 60 seconds
4. If successful: clears screen, displays the actual framebuffer image, waits 20 seconds, sleeps
5. If error: leaves the debug info on screen and sleeps

**Security**: WiFi password is never displayed (shown as `[set]`). SSID and other safe info is shown to aid debugging.
