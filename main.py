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
# from digitalio import DigitalInOut, Direction, Pull
from digitalio import DigitalInOut, Direction


# led = DigitalInOut(board.D13)
# led.direction = Direction.OUTPUT

stepper_dir = DigitalInOut(board.D12)
stepper_dir.direction = Direction.OUTPUT
# stepper_step = DigitalInOut(board.D9)
# stepper_step.direction = Direction.OUTPUT
stepper_step = pulseio.PWMOut(
    board.D9, duty_cycle=0, frequency=5, variable_frequency=True)

led = pulseio.PWMOut(
    board.D13, duty_cycle=0, frequency=50, variable_frequency=True)


def stepper_run(freq=200):
    """Run Stepper Motor with given frequency."""
    stepper_step.frequency = freq
    stepper_step.duty_cycle = 65535 // 2
    led_freq = freq // 10
    if freq < 10:
        led_freq = freq
    led.frequency = led_freq
    led.duty_cycle = 65535 // 2
    # stepper_step.duty_cycle = 32767
    print("stepper run @{}Hz".format(stepper_step.frequency))


def stepper_fade_to(freq_target=2000, freq_start=1000):
    """
    Run Stepper Motor with given frequency.

    QSH2818-32-07-006
    Maximum microstep velocity = Fullstep threshold = RPS 5.817
    Maximum fullstep velocity = RPS 12.875
    (1  RPS  =  1  revolution  per  second)

    RPM = freq/(200*16/60)
    RPS = freq/(steps_revolution*microsteps)
    RPS = freq/(200*16)
    250000/(200*16/60) = 4687,5 RPM = 78,125 RPS

    """
    if freq_target > 250000:
        freq_target = 250000
    stop_at_end = False
    if freq_target == 0:
        stop_at_end = True
        freq_target = 2
    step = 1
    if freq_target < freq_start:
        step *= -1
    # stepper_step.duty_cycle = 32767
    stepper_step.frequency = freq_start
    stepper_step.duty_cycle = 65535 // 2
    led.duty_cycle = 65535 // 2
    led_freq = freq_target // 10
    if freq_target < 10:
        led_freq = freq_target
        if freq_target == 0:
            led_freq = 2
    led.frequency = led_freq
    print("stepper start fade to {}Hz {}RPS".format(
        freq_target, freq_target/(200*16)))
    # delay_time = 0
    # if abs(freq_start - freq_target) > 100000:
    #     delay_time = 0.001
    # for freq in range(freq_start, freq_target, 10):
    for freq in range(freq_start, freq_target, step):
        stepper_step.frequency = freq
        # print(".", end="")
        # led.frequency = freq // 1000
        if (freq % 100) == 0:
            print(".", end="")
            # print(". {}Hz".format(stepper_step.frequency))
        # time.sleep(delay_time)
    print("")
    if stop_at_end:
        stepper_stop()
    else:
        print("stepper running at {}Hz {}RPS".format(
            stepper_step.frequency, stepper_step.frequency/(200*16)))


def stepper_stop():
    """Stop Stepper Motor."""
    stepper_step.duty_cycle = 0
    stepper_step.frequency = 10
    led.duty_cycle = 0
    print("stepper stopped.")


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
                stepper_fade_to(
                    freq_target=freq_new, freq_start=stepper_step.frequency)
            else:
                freq_new = parse_value(input_string, int)
                if freq_new == 0:
                    stepper_stop()
                else:
                    stepper_run(freq_new)
        else:
            stepper_stop()
        print(">> ", end="")


##########################################
#
#

print("start stepper with 100Hz")
stepper_run(300)


print(42 * '*')
print("loop..")
if supervisor.runtime.serial_connected:
    print("type frequency:")
while True:
    check_input()


# while True:
#     for i in range(100):
#         # PWM LED up and down
#         if i < 50:
#             led.duty_cycle = int(i * 2 * 65535 / 100)  # Up
#         else:
#             led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
#         time.sleep(0.01)
