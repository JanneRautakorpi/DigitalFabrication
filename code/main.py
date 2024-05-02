import utime
from machine import I2C, Pin
from pico_i2c_lcd import I2cLcd
from rotary_irq_rp2 import RotaryIRQ

# Constants
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
PIN_SDA = 26
PIN_SCL = 27
PIN_R1_CLK = 15
PIN_R1_DT = 14
PIN_R2_CLK = 16
PIN_R2_DT = 17
PIN_BUTTON = 7
SLEEP_TIME = 50  # in ms


def init_lcd(sda_pin, scl_pin):
    '''
    Initialization for LCD display.
    Parameters:
    sda_pin
    scl_pin

    Return:
    lcd object
    '''
    i2c = I2C(1, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    lcd.putstr("Welcome to Measurement Fox <3")
    return lcd

def init_rotary(pin_clk, pin_dt):
    '''
    Initialization for rotary encoder.
    Parameters: 
    pin_clk
    pin_dt

    Return:
    instance of RotaryIRQ
    '''
    return RotaryIRQ(pin_num_clk=Pin(pin_clk),
                     pin_num_dt=Pin(pin_dt),
                     pull_up=True,
                     range_mode=RotaryIRQ.RANGE_UNBOUNDED)

def main():
    '''
    Main function where the program loops.
    No parameters.
    No return  values.
    '''
    lcd = init_lcd(PIN_SDA, PIN_SCL)
    r1 = init_rotary(PIN_R1_CLK, PIN_R1_DT)
    r2 = init_rotary(PIN_R2_CLK, PIN_R2_DT)
    button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_UP)
    distance_constant = 10
    val_old1, val_old2 = r1.value(), r2.value()

    utime.sleep_ms(2000)

    lcd.clear()
    lcd.putstr("Distance pushed: 0.00   meters")

    while True:
        val_new1, val_new2 = r1.value(), r2.value()

        if val_old1 != val_new1 or val_old2 != val_new2:
            val_old1, val_old2 = val_new1, val_new2
            result = (val_new1 + val_new2) / 2
            print(f'Values = {val_new1}, {val_new2}')
            print(f'Result = {result}')
            distance = result / distance_constant
            lcd.move_to(0, 1)
            text = f"{distance:.2f}"
            if (text[0] != '-'):
                text = " " + text

            lcd.putstr(text)

        if not button.value():
            print('Button pressed')
            r1.reset()
            r2.reset()

        utime.sleep_ms(SLEEP_TIME)

#if __name__ == "__main__":
main()
