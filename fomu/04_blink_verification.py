#!/usr/bin/env python3
"""
Blink red, then green, then blue, then nothing
"""

import enum
import os

import nmigen
import nmigen.asserts
import nmigen.back.pysim
import nmigen.build
import nmigen.cli


@enum.unique
class RGB(enum.Enum):
    NONE = 0
    R = 1
    G = 2
    B = 3


# this time make our own blink
class Blink(nmigen.Elaboratable):
    def __init__(self, hz=2):
        self.hz = int(hz)
        self.active_led = nmigen.Signal(RGB)
        self.r = nmigen.Signal()
        self.g = nmigen.Signal()
        self.b = nmigen.Signal()

    def elaborate(self, platform: nmigen.build.Platform) -> nmigen.Module:
        m = nmigen.Module()

        # get the clock frequency (in this case 48 MHz)
        if hasattr(platform, 'default_clk_frequency'):
            clk_freq = platform.default_clk_frequency
        else:
            clk_freq = 48000000

        # count up on sync domain to cycle leds
        timer = nmigen.Signal(range(int(clk_freq//self.hz)), reset=int(clk_freq//self.hz) - 1)
        with m.If(timer == 0):
            m.d.sync += timer.eq(timer.reset)
            m.d.sync += self.active_led.eq(self.active_led + 1)
        with m.Else():
            m.d.sync += timer.eq(timer - 1)

        # switch case to enable leds
        with m.Switch(self.active_led):
            with m.Case(RGB.R):
                m.d.comb += [
                    self.r.eq(1),
                    self.g.eq(0),
                    self.b.eq(0),
                ]
            with m.Case(RGB.G):
                m.d.comb += [
                    self.r.eq(0),
                    self.g.eq(1),
                    self.b.eq(0),
                ]
            with m.Case(RGB.B):
                m.d.comb += [
                    self.r.eq(0),
                    self.g.eq(0),
                    self.b.eq(1),
                ]
            with m.Default():
                m.d.comb += [
                    self.r.eq(0),
                    self.g.eq(0),
                    self.b.eq(0),
                ]
        # or store 4 bits, cycle through and cat them together
        return m

    def ports(self):
        """Define what signals to output to the simulation"""
        return [self.active_led, self.r, self.g, self.b]


m = nmigen.Module()
m.submodules.blink = blink = Blink(hz=int(24E6))

m.d.comb += [
    nmigen.asserts.Cover(
        (nmigen.asserts.Past(blink.active_led) == RGB.NONE) &
        (blink.active_led == RGB.R)),
]

parser = nmigen.cli.main_parser()
args = parser.parse_args()

# run this with:
# >> python3 04_blink_verification.py generate -t il > toplevel.il
# >> sby -f 04_blink_verification.sby
nmigen.cli.main_runner(parser, args, m, ports=[] + blink.ports())
