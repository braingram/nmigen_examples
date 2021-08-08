#!/usr/bin/env python3

import os

import nmigen

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

# import the simple 'blink' example
from nmigen_boards.test.blinky import Blinky


# elaborate the blinky program, build the resulting logic and program
# the fomu
FomuPlatform().build(Blinky(), do_program=True)
