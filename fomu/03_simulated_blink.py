#!/usr/bin/env python3
"""
Blink red, then green, then blue, then nothing
"""

import enum
import os

import nmigen
import nmigen.back.pysim
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
    def __init__(self, hz=2):
        self.hz = int(hz)
        self.active_led = nmigen.Signal(RGB)
        self.r = nmigen.Signal()
        self.g = nmigen.Signal()
        self.b = nmigen.Signal()

    def elaborate(self, platform: nmigen.build.Platform) -> nmigen.Module:
        m = nmigen.Module()

        # request the rgb led pins from the platform
        #rgb = platform.request('rgb_led')

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


# instead of building, run this in a simulator
m = Blink(hz=int(24E6))  # run the lights fast to reduce the simulation time


# define what to simulate
def sync_process():
    # just run for many steps
    for i in range(10):
        yield

sim = nmigen.back.pysim.Simulator(m)
sim.add_clock(1 / 48E6, domain='sync')
sim.add_sync_process(sync_process, domain='sync')

with sim.write_vcd("test.vcd", "test.gtkw", traces=m.ports()):
    sim.run()
