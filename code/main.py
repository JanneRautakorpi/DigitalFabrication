import utime

import machine
from machine import I2C, Pin
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

import sys
from rotary_irq_rp2 import RotaryIRQ

import time

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# i2c lcd
PIN_SDA = 26
PIN_SCL = 27

# rotary encoder
PIN_CLK1 = Pin(15)
PIN_DT1 = Pin(14)
PIN_CLK2 = Pin(16)
PIN_DT2 = Pin(17)

PIN_BUTTON = Pin(7, Pin.IN, Pin.PULL_UP)

SLEEP_TIME = 50 # in ms

def main():
    print("Running main")
    i2c = I2C(1, sda=machine.Pin(PIN_SDA), scl=machine.Pin(PIN_SCL), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)    
    lcd.putstr("welcome to measurement fox <3")
    
    r = RotaryIRQ(pin_num_clk=PIN_CLK1,
              pin_num_dt=PIN_DT1,
              pull_up=True,
              range_mode=RotaryIRQ.RANGE_UNBOUNDED)
    
    r2 = RotaryIRQ(pin_num_clk=PIN_CLK2,
              pin_num_dt=PIN_DT2,
              pull_up=True,
              range_mode=RotaryIRQ.RANGE_UNBOUNDED)
    
    distance_constant = 1

    val_old = r.value()
    val_old2 = r2.value()
    while True:
        val_new = r.value()
        val_new2 = r2.value()

        if (val_old != val_new) or (val_old2 != val_new2):
            val_old = val_new
            val_old2 = val_new2
            result = (val_new + val_new2) / 2
            print('values =', val_new, "ja", val_new2)
            print('result =', result)
            distance = result / distance_constant
            lcd.clear()
            lcd.putstr(f"distance pushed:  {distance:.2f} meters")

        if PIN_BUTTON.value() != 1:
            print('button pressed')
            r.reset()
            r2.reset()

        utime.sleep_ms(SLEEP_TIME)

#if __name__ == "__main__":
main()
