import utime

import machine
from machine import I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

import sys
from rotary_irq_rp2 import RotaryIRQ

import time

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

def test_main():
    #Test function for verifying basic functionality
    print("Running test_main")
    i2c = I2C(0, sda=machine.Pin(20), scl=machine.Pin(21), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)    
    lcd.putstr("welcome to measurement fox <3")
    
    while True:
        print("test")
    
    r = RotaryIRQ(pin_num_clk=14,
              pin_num_dt=15,
              reverse=False,
              pull_up=True,
              range_mode=RotaryIRQ.RANGE_UNBOUNDED)
    
    distance_constant = 2.4

    val_old = r.value()
    while True:
        val_new = r.value()

        if val_old != val_new:
            val_old = val_new
            print('result =', val_new)
            lcd.clear()
            distance = val_new / distance_constant
            lcd.putstr("distance pushed:  {:.2f} meters".format(distance))

        time.sleep_ms(50)

#if __name__ == "__main__":
test_main()