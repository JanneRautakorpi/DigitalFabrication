import sys
import uasyncio as asyncio
from rotary_irq_rp2 import RotaryIRQ
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

distance = 0

# Use heartbeat to keep event loop not empty
async def heartbeat(lcd):
    while True:
        lcd.clear()
        lcd.putstr("distance pushed:  {:.2f} meters".format(distance))
        await asyncio.sleep_ms(1000)

event = asyncio.Event()


def callback():
    event.set()


async def main():
    r = RotaryIRQ(pin_num_clk=15,
                  pin_num_dt=14)
    r.add_listener(callback)

    i2c = I2C(1, sda=machine.Pin(PIN_SDA), scl=machine.Pin(PIN_SCL), freq=800000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)    
    lcd.putstr("welcome to measurement fox <3")
    
    asyncio.create_task(heartbeat(lcd))
    while True:
        await event.wait()
        result = r.value()
        print('result =', result)
        global distance
        distance = result
        event.clear()
        #lcd.clear()
        #lcd.putstr("distance pushed:  {:.2f} meters".format(result))

try:
    print("haloo")
    asyncio.run(main())
except (KeyboardInterrupt, Exception) as e:
    print('Exception {} {}\n'.format(type(e).__name__, e))
finally:
    ret = asyncio.new_event_loop()  # Clear retained uasyncio state
