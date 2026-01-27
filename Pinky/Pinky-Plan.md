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

