# imports
from machine import Pin, ADC
import math
import time

#######################################
# Pin and constant definitions
#######################################
pixels = [0,1,2,3,4,5,6,7]
digits = [8,9,10,11]
button = 16
reader = 26

pixels_pins = []
Decimal_pin = None
digit_pins = []
button_pin = None
reader_pin = ADC(reader)

DISPLAY_COUNT = 4

#######################################
# Global variables
#######################################
display_value = 0
last_button_time_stamp = 0
display_timer = None
current_display_index = DISPLAY_COUNT -1
DECIMAL_PRECISION = 3



nums_map = [
    0x40,  # 0
    0x79,  # 1
    0x24,  # 2
    0x30,  # 3
    0x19,  # 4
    0x12,  # 5
    0x02,  # 6
    0x78,  # 7
    0x00,  # 8
    0x10,  # 9
    0x08,  # A
    0x03,  # B
    0x46,  # C
    0x21,  # D
    0x06,  # E
    0x0E,  # F
    0x7F   # Empty
]

# Function to read the ADC pin and
# to convert the digital value to a voltage level in the 0-3.3V range
# This function updates the value of the display_value global variable
def read_analogue_voltage(pin):  # We can use the pin parameter if needed
    global last_button_time_stamp

    cur_button_ts = time.ticks_ms()
    button_press_delta = cur_button_ts - last_button_time_stamp
    if button_press_delta > 200:
        last_button_time_stamp = cur_button_ts
        global display_value

        digital_Reading = reader_pin.read_u16()
        display_value = (digital_Reading / 2**16) * 3300
        print(str(round(display_value, 1)) + " mV")

# Function to disable timer that triggers scanning 7 segment displays
def disable_display_timer():
    global display_timer
    display_timer.deinit()

# Function to enable timer that triggers scanning 7 segment displays
def enable_display_timer():
    global display_timer
    display_timer.init(period=30, mode=machine.Timer.PERIODIC, callback=scan_display)

# Function to handle scanning 7 segment displays
# Display the value stored in the display_value global variable
# on available 7-segment displays
def scan_display(timer_int):
    global current_display_index, display_value

    digit = int((display_value // math.pow(10, current_display_index))) % 10

    display_digit(digit, current_display_index, 
        current_display_index == DECIMAL_PRECISION and 0 != DECIMAL_PRECISION)

    current_display_index -= 1
    if current_display_index < 0:
        current_display_index = DISPLAY_COUNT -1

# Function display the given value on the display with the specified index
# dp_enable specifies if the decimal point should be on or off
def display_digit(digit_value, digit_index, dp_enable=False):
    if digit_value < 0 or digit_value > len(nums_map):
        return

    for pin in digit_pins:
        pin.value(0)

    mask = nums_map[digit_value]
    for i in range(7):
        pixels_pins[i].value((mask >> i) & 1)

    pixels_pins[7].value(1 if dp_enable == False else 0)


    if digit_index == -1:
        for pin in digit_pins:
            pin.value(1)

    elif 0 <= digit_index < DISPLAY_COUNT:
        digit_pins[digit_index].value(1)


# Function to test avaiable 7-segment displays
def display_value_test():
    global display_value

    disable_display_timer()
    current_display_index = 0

    for i in range(0, len(nums_map)):
        display_digit(i, -1, i % 2 != 0)
        time.sleep(0.5)

    for i in range(0, len(nums_map)):
        display_digit(i, DISPLAY_COUNT - 1 - (i % DISPLAY_COUNT), True)
        time.sleep(0.5)        

    display_digit(16, -1, False)
    enable_display_timer()

def count_display_value(timer_int):
    global display_value
    display_value += 1
    if display_value > 9999:
        display_value = 0

# Function to setup GPIO/ADC pins, timers and interrupts
def setup():
    global display_timer
    for i in pixels:
        pixels_pins.append(Pin(i, Pin.OUT))

    for i in digits:
        digit_pins.append(Pin(i, Pin.OUT))

    button_pin = Pin(button, Pin.IN, Pin.PULL_UP)
    button_pin.irq(trigger=Pin.IRQ_RISING, handler=read_analogue_voltage)

    display_timer = machine.Timer()
    enable_display_timer()

if __name__ == '__main__':
    setup()
    # display_value_test()