#!/usr/bin/env python3
"""
Blink red, then green, then blue, then nothing
"""

import enum
import os

import nmigen
import nmigen.build

# reuse the FOMU_REV environment variable from the fomu workshop to detect
# the board version to import the correct 'Platform'
# the Platform contains:
# - LEDResources: 1 led (used in blink below)
# - Resource: clk48
# - RGBLEDResource: r, g, b
# - DirectUSBResource: d_p, d_n
#   etc...
if os.environ.get('FOMU_REV', 'pvt') == 'pvt':
    from nmigen_boards.fomu_pvt import FomuPVTPlatform as FomuPlatform
else:
    from nmigen_boards.fomu_hacker import FomuHackerPlatform as FomuPlatform


@enum.unique
class RGB(enum.Enum):
    NONE = 0
    R = 1
    G = 2
    B = 3

# this time make our own blink
class Blink(nmigen.Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform: nmigen.build.Platform) -> nmigen.Module:
        m = nmigen.Module()

        # request the rgb led pins from the platform
        rgb = platform.request('rgb_led')

        # get the clock frequency (in this case 48 MHz)
        clk_freq = platform.default_clk_frequency

        active_led = nmigen.Signal(RGB)

        # count up on sync domain to cycle leds
        timer = nmigen.Signal(range(int(clk_freq//2)), reset=int(clk_freq//2) - 1)
        with m.If(timer == 0):
            m.d.sync += timer.eq(timer.reset)
            m.d.sync += active_led.eq(active_led + 1)
        with m.Else():
            m.d.sync += timer.eq(timer - 1)

        # switch case to enable leds
        with m.Switch(active_led):
            with m.Case(RGB.R):
                m.d.comb += [
                    rgb.r.o.eq(1),
                    rgb.g.o.eq(0),
                    rgb.b.o.eq(0),
                ]
            with m.Case(RGB.G):
                m.d.comb += [
                    rgb.r.o.eq(0),
                    rgb.g.o.eq(1),
                    rgb.b.o.eq(0),
                ]
            with m.Case(RGB.B):
                m.d.comb += [
                    rgb.r.o.eq(0),
                    rgb.g.o.eq(0),
                    rgb.b.o.eq(1),
                ]
            with m.Default():
                m.d.comb += [
                    rgb.r.o.eq(0),
                    rgb.g.o.eq(0),
                    rgb.b.o.eq(0),
                ]
        # or store 4 bits, cycle through and cat them together
        return m


# elaborate the program, build the resulting logic and program
# the fomu
FomuPlatform().build(Blink(), do_program=True)
