#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CircuitPython

"""
Simple Test for Stepper Motor with SilentStepStick Driver.

source:
based on:
https://learn.adafruit.com/circuitpython-essentials/circuitpython-pwm

This test will
"""

import time

import supervisor
import board
import pulseio
import rotaryio
# from digitalio import DigitalInOut, Direction, Pull
# from digitalio import DigitalInOut, Direction
import digitalio

import terminalio
import displayio
from adafruit_display_text import label
from adafruit_ssd1331 import SSD1331

from stepper import MyStepper

# led = DigitalInOut(board.D13)
# led.direction = digitalio.Direction.OUTPUT

mystepper = MyStepper(
    pin_direction=board.D12,
    pin_step=board.D9,
    pin_led=board.D13,
    steps_per_revolution=200,
    microsteps=16
)


button_back = digitalio.DigitalInOut(board.A0)
button_back.pull = digitalio.Pull.UP
button_ok = digitalio.DigitalInOut(board.A1)
button_ok.pull = digitalio.Pull.DOWN
rot_encoder = rotaryio.IncrementalEncoder(board.A2, board.A3)
rot_encoder_lastvalue = 0

button_run = digitalio.DigitalInOut(board.D11)
button_run.pull = digitalio.Pull.UP


# display
displayio.release_displays()
spi = board.SPI()
tft_cs = board.D2
tft_dc = board.A4
tft_res = board.A5

display_bus = displayio.FourWire(
    spi, command=tft_dc, chip_select=tft_cs, reset=tft_res
)

display = SSD1331(display_bus, width=96, height=64)
display.rotation = 180

# splash = displayio.Group(max_size=10)
# display.show(splash)

# globals
button_back_state = False

##########################################


# stepper


# buttons

def handle_buttons():
    """Check Button Inputs."""
    global rot_encoder_lastvalue
    global button_back_state

    # if button_back.value is not button_back_state:
    #     button_back_state = button_back.value
    if not button_back.value:
        print("reset encoder position")
        rot_encoder.position = 0

    if button_ok.value:
        # print("button ok")
        if mystepper.speed_rps_current is not mystepper.speed_rps_target:
            mystepper.fade_to_rps(mystepper.speed_rps_target)

    # if button_run.value is not mystepper.run:
    if not button_run.value:
        print("toggle mystepper")
        mystepper.toggle()

    if rot_encoder.position is not rot_encoder_lastvalue:
        diff = rot_encoder.position - rot_encoder_lastvalue
        if rot_encoder.position > 100:
            # simple *step size multiply*
            new_pos = rot_encoder.position + (diff*10)
            # foce 10-steps
            new_pos = (new_pos // 10) * 10
            rot_encoder.position = new_pos
        rot_encoder_lastvalue = rot_encoder.position
        mystepper.speed_rpm_target = rot_encoder.position
        mystepper.speed_rps_target = mystepper.speed_rpm_target / 60
        print("mystepper.speed_rps_target: {}".format(
            mystepper.speed_rps_target))

    # if time.monotonic() % 1 == 0:
    #     print("rot_encoder: {}".format(rot_encoder.position))


# debug menu
def parse_value(input_string, parse_function, default_value=0):
    """Parse input values."""
    result = default_value
    try:
        result = parse_function(input_string)
    except ValueError as e:
        print(
            "Exception parsing '{}': "
            "".format(input_string),
            e
        )
    return result


def check_input():
    """Check Input."""
    if supervisor.runtime.serial_bytes_available:
        input_string = input()
        if input_string:
            if "f" in input_string:
                freq_new = parse_value(input_string[1:], int)
                mystepper.fade_to(freq_target=freq_new)
            else:
                freq_new = parse_value(input_string, int)
                if freq_new == 0:
                    mystepper.stop()
                else:
                    mystepper.run(freq_new)
        else:
            mystepper.stop()
        print(">> ", end="")


# display
def update_display():
    """Update Display."""
    text = (
        "{:+.2f} RPS\n"
        "{:+.2f} RPM"
        "".format(
            mystepper.speed_rps_target,
            mystepper.speed_rps_target*60
        )
    )
    text_area = label.Label(
        terminalio.FONT, text=text, color=0xFFFFFF, x=12, y=32)
    # splash.append(text_area)
    display.show(text_area)


##########################################
#
#

def main(debugmenu=False):
    """Main."""
    if debugmenu:
        check_input()
    handle_buttons()
    update_display()

# print("start stepper with 100Hz")
# stepper_run(300)


print(42 * '*')
print("loop..")
if supervisor.runtime.serial_connected:
    print("type frequency:")
while True:
    main(debugmenu=supervisor.runtime.serial_connected)


# while True:
#     for i in range(100):
#         # PWM LED up and down
#         if i < 50:
#             led.duty_cycle = int(i * 2 * 65535 / 100)  # Up
#         else:
#             led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
#         time.sleep(0.01)
