import machine
import utime
from machine import I2C, Pin
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

import sys
from rotary_irq_rp2 import RotaryIRQ


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

DEBOUNCE_TIME = 500 # in ms

def main():
    print("Running main")
    i2c = I2C(1, sda=machine.Pin(PIN_SDA), scl=machine.Pin(PIN_SCL), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)    
    lcd.putstr("welcome to measurement fox <3")
    
    r = RotaryIRQ(pin_num_clk=PIN_CLK1,
              pin_num_dt=PIN_DT1,
              pull_up=False,
              range_mode=RotaryIRQ.RANGE_UNBOUNDED)
    
    distance_constant = 1

    val_old = r.value()
    while True:
        val_new = r.value()

        if val_old != val_new:
            val_old = val_new
            print('values =', val_new)
            distance = val_new / distance_constant
            lcd.clear()
            lcd.putstr("distance pushed:  {:.2f} meters".format(distance))

        #if PIN_BUTTON.value() != 1:
        #    print('button pressed')
        #    r.reset()

        utime.sleep_ms(DEBOUNCE_TIME)

#if __name__ == "__main__":
main()
