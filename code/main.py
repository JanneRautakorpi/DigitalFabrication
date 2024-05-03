"""
This module contains the main code for the Measurement Fox project.
It initializes the LCD display and rotary encoders, and provides functions
for handling user input and displaying information on the LCD.
"""

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
PIN_R2_CLK = 15
PIN_R2_DT = 14
PIN_R1_CLK = 16
PIN_R1_DT = 17
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
    "wheel_mode": 0, # 0 both, 1 left, 2 right
    "oldResult": 0
    }

    lcd = init_lcd(PIN_SDA, PIN_SCL)
    r1 = init_rotary(PIN_R1_CLK, PIN_R1_DT)
    r2 = init_rotary(PIN_R2_CLK, PIN_R2_DT)
    button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_UP)
    state["wheel_mode"] = False

    val_old1, val_old2 = r1.value(), r2.value()

    first_loop = True
    button_held_for = 0

    utime.sleep_ms(2000)

    reset_lcd(lcd, 0.0)

    button_pressed = False
    first_loop = False
    result = 0
    i = 0

    while True:
        val_new1, val_new2 = r1.value(), r2.value()

        if (val_old1 != val_new1 or val_old2 != val_new2) and i % LCD_UPDATE == 0:
            val_old1, val_old2 = val_new1, val_new2

            if state["wheel_mode"] == 0:
                result = (val_new1 + val_new2) / 2

            elif state["wheel_mode"] == 1:
                result = val_new1

            elif state["wheel_mode"] == 2:
                result = val_new2

            print(f'Values = {val_new1}, {val_new2}')
            print(f'Result = {result}')
            distance = calculate_distance(result, state)
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
                disable_rotaries([r1, r2])
                state["oldResult"] += result
                r1.reset()
                r2.reset()
                result = 0
                enter_menu(lcd, button, button_held_for, state)
                enable_rotaries(r1, r2, state)
                print('exiting menu')
                distance = calculate_distance(result, state)
                reset_lcd(lcd, distance)
                first_loop = True

        # release
        if button.value() and button_pressed and not first_loop:
            button_pressed = False
            button_held_for = 0

            print("release")

            r1.reset()
            r2.reset()
            result = 0
            state["oldResult"] = 0

        # release after exiting menu
        if button.value() and button_pressed and first_loop:
            first_loop = False
            button_pressed = False
            button_held_for = 0

            print("first release")

        i = (i + 1) % LCD_UPDATE
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
        wheel_mode (int): Which wheels are currently used for measurement.

    Returns:
        None
    """
    mode_select = True
    button_pressed = True
    first_loop = True

    lcd_put_mode_text(lcd, state)

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

            state["wheel_mode"] = (state["wheel_mode"] + 1) % 3
            lcd_put_mode_text(lcd, state)

        # release after entering menu
        if button.value() and button_pressed and first_loop:
            first_loop = False
            button_pressed = False
            button_held_for = 0

            print("first release")

        utime.sleep_ms(SLEEP_TIME)

    print('Button held for 1 second')

def get_mode_string(state):
    """
    Returns the string representation of the current wheel mode.

    Args:
        state (dict): The state object containing the current wheel mode.

    Returns:
        str: The string representation of the current wheel mode.
    """
    modes = ["Both wheels", "Left wheel", "Right wheel"]
    return modes[state["wheel_mode"]]

def disable_rotaries(rotaries):
    """
    Disables the IRQ (interrupt request) for the given rotaries.

    Args:
        rotaries (list): A list of rotary encoders.

    Returns:
        None
    """
    for r in rotaries:
        r._hal_disable_irq()

def enable_rotaries(r1, r2, state):
    """
    Enable or disable the rotary encoders based on the wheel mode specified in the state dictionary.

    Parameters:
    - r1: The first rotary encoder object.
    - r2: The second rotary encoder object.
    - state: Dictionary containing the current state.

    Returns:
    None
    """
    if state["wheel_mode"] == 0:
        r1._hal_enable_irq()
        r2._hal_enable_irq()

    elif state["wheel_mode"] == 1:
        r1._hal_enable_irq()
        r2._hal_disable_irq()

    elif state["wheel_mode"] == 2:
        r1._hal_disable_irq()
        r2._hal_enable_irq()

def calculate_distance(result, state):
    """
    Calculates the distance measured based on the result from rotary encoders and state.

    Parameters:
    result (float): The result value.
    state (dict): The state dictionary containing the old result.

    Returns:
    float: The calculated distance.
    """
    return (state["oldResult"] + result) * DISTANCE_CONSTANT

def lcd_put_mode_text(lcd, state):
    """
    Displays the current mode on the LCD screen.

    Args:
        lcd: The LCD object used for displaying text.
        state: State containing the mode.

    Returns:
        None
    """
    lcd.clear()
    lcd.putstr("Mode:")
    lcd.move_to(0, 1)
    lcd.putstr(get_mode_string(state))

#if __name__ == "__main__":
main()
