"""
This module contains the main code for the Measurement Fox project.
It initializes the LCD display and rotary encoders,and provides functions
for handling user input and displaying information on the LCD.
"""

import utime # type: ignore
from machine import I2C, Pin # type: ignore
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
MODE_HOLD_TIME = 1000
DISTANCE_CONSTANT = 4.90/468
LCD_UPDATE = 10 # update display every n loop

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

    state = {
    "single_wheel_mode": False
    }

    lcd = init_lcd(PIN_SDA, PIN_SCL)
    r1 = init_rotary(PIN_R1_CLK, PIN_R1_DT)
    r2 = init_rotary(PIN_R2_CLK, PIN_R2_DT)
    button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_UP)
    state["single_wheel_mode"] = False
    distance_constant_calculated = DISTANCE_CONSTANT

    val_old1, val_old2 = r1.value(), r2.value()

    first_loop = True
    button_held_for = 0

    utime.sleep_ms(2000)

    reset_lcd(lcd, 0.0)

    button_pressed = False
    first_loop = False

    while True:
        val_new1, val_new2 = r1.value(), r2.value()

        if val_old1 != val_new1 or val_old2 != val_new2:
            val_old1, val_old2 = val_new1, val_new2
            result = (val_new1 + val_new2) / 2
            print(f'Values = {val_new1}, {val_new2}')
            print(f'Result = {result}')
            distance = result * distance_constant_calculated
            lcd.move_to(0, 1)
            text = f"{distance:.2f}"
            if text[0] != '-':
                text = " " + text

            lcd.putstr(text)
        

        # press
        if not button.value() and not button_pressed and not first_loop:
            button_pressed = True

            print("Button pressed")

        # hold
        if not button.value() and button_pressed and not first_loop:
            button_held_for += SLEEP_TIME

            print("hold for", button_held_for)

            if button_held_for >= MODE_HOLD_TIME:
                button_held_for = 0
                print('entering menu')
                enter_menu(lcd, button, button_held_for, state)
                print('exiting menu')
                distance_constant_calculated = DISTANCE_CONSTANT * 2 if state["single_wheel_mode"] else DISTANCE_CONSTANT
                result = (val_new1 + val_new2) / 2
                distance = result * distance_constant_calculated
                reset_lcd(lcd, distance)
                first_loop = True

        # release
        if button.value() and button_pressed and not first_loop:
            button_pressed = False
            button_held_for = 0

            print("release")

            r1.reset()
            r2.reset()

        # release after exiting menu
        if button.value() and button_pressed and first_loop:
            first_loop = False
            button_pressed = False
            button_held_for = 0

            print("first release")

        utime.sleep_ms(SLEEP_TIME)


def reset_lcd(lcd, distance):
    """
    Clears the LCD display and sets the initial text.

    Parameters:
    lcd (object): The LCD object used for displaying information.

    Returns:
    None
    """
    text = f"{float(distance):.2f}"
    if text[0] != '-':
        text = " " + text
    lcd.clear()
    lcd.putstr(f"Distance pushed:{text}   meters")



def enter_menu(lcd, button, button_held_for, state):
    """
    Enters the menu and allows the user to toggle the single wheel mode.

    Args:
        lcd (object): The LCD object used for displaying information.
        button (object): The button object used for user input.
        button_held_for (int): The duration for which the button has been held.
        single_wheel_mode (bool): The current state of the single wheel mode.

    Returns:
        None
    """
    mode_select = True
    button_pressed = True
    first_loop = True

    lcd.clear()
    enabled = state["single_wheel_mode"]
    lcd.putstr(f"Single wheel    mode: {enabled}")

    while mode_select:
        # press
        if not button.value() and not button_pressed and not first_loop:
            button_pressed = True

            print("Button pressed in menu")

        # hold
        if not button.value() and button_pressed and not first_loop:
            button_held_for += SLEEP_TIME

            print("hold for", button_held_for)

            if button_held_for >= MODE_HOLD_TIME:
                mode_select = False

        # release
        if button.value() and button_pressed and not first_loop:
            button_pressed = False
            button_held_for = 0

            print("release")

            state["single_wheel_mode"] = not state["single_wheel_mode"]
            lcd.clear()
            enabled = state["single_wheel_mode"]
            lcd.putstr(f"Single wheel mode: {'Enabled' if enabled else 'Disabled'}")

        # release after entering menu
        if button.value() and button_pressed and first_loop:
            first_loop = False
            button_pressed = False
            button_held_for = 0

            print("first release")

        utime.sleep_ms(SLEEP_TIME)

    print('Button held for 1 second')


#if __name__ == "__main__":
main()
