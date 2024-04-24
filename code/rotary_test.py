# MIT License (MIT)
# Copyright (c) 2021 Mike Teachman
# https://opensource.org/licenses/MIT

# example for MicroPython rotary encoder

import sys
from rotary_irq_rp2 import RotaryIRQ

import time


r = RotaryIRQ(pin_num_clk=7,
              pin_num_dt=8,
              reverse=False,
              pull_up=True,
              range_mode=RotaryIRQ.RANGE_UNBOUNDED)

val_old = r.value()
while True:
    val_new = r.value()

    if val_old != val_new:
        val_old = val_new
        print('result =', val_new)

    time.sleep_ms(50)
