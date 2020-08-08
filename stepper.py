#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CircuitPython
"""Stepper Motor."""

__doc__ = """
stepper.py

handling for stepper motors.
"""

import time

import board
import digitalio
import pulseio

##########################################
if __name__ == '__main__':
    print()
    print(42 * '*')
    print(__doc__)
    print(42 * '*')
    print()


##########################################

class MyStepper():
    """MyStepper."""

    STATE_STANDBY = 0
    STATE_FADING = 1
    STATE_RUNNING = 2

    def __init__(
            self,
            *,
            pin_direction=board.D12,
            pin_step=board.D9,
            pin_led=board.D13,
            steps_per_revolution=200,
            microsteps=16,
    ):
        """Init."""
        super(MyStepper, self).__init__()
        self.pin_direction = pin_direction
        self.pin_step = pin_step
        self.pin_led = pin_led
        self.steps_per_revolution = steps_per_revolution
        self.microsteps = microsteps

        # TODO: s-light implement calculation on value change: property
        self.freq_steps_factor = (self.steps_per_revolution*self.microsteps)

        self.speed_rps_current = 0
        self.speed_rps_target = 0

        self.stepper_run = False
        self.state = False

        self.stepper_dir = digitalio.DigitalInOut(self.pin_direction)
        self.stepper_dir.direction = digitalio.Direction.OUTPUT
        # stepper_step = digitalio.DigitalInOut(board.D9)
        # stepper_step.direction = digitalio.Direction.OUTPUT
        self.stepper_step = pulseio.PWMOut(
            self.pin_step,
            duty_cycle=0,
            frequency=1,
            variable_frequency=True)

        if self.pin_led:
            self.led = pulseio.PWMOut(
                self.pin_led,
                duty_cycle=0,
                frequency=1,
                variable_frequency=True)

    ##########################################
    # fadeing

    def fade_to_rpm(self, rpm=1):
        """Run Stepper Motor with given speed in RPM."""
        self.fade_to_rps(rpm/60)

    def fade_to_rps(self, rps=(1/60)):
        """
        Run Stepper Motor with given speed in RPS.

        QSH2818-32-07-006
        Maximum microstep velocity = Fullstep threshold = RPS 5.817
        Maximum fullstep velocity = RPS 12.875
        (1  RPS  =  1  revolution  per  second)

        RPM = freq/(200*16/60)
        RPS = freq/(steps_revolution*microsteps)
        RPS = freq/(200*16)
        250000/(200*16/60) = 4687,5 RPM = 78,125 RPS

        RPS = freq/(200*16)
        RPS = freq/(200*16) | * (200*16)
        RPS*(200*16) = freq
        """
        freq_new = rps * self.freq_steps_factor
        self.fade_to(freq_target=freq_new)

    def fade_to(self, freq_target=2000, freq_start=None):
        """Run Stepper Motor with given frequency."""
        freq_target = int(freq_target)
        if not freq_start:
            freq_start = int(self.stepper_step.frequency)

        if freq_target > 250000:
            freq_target = 250000
        stop_at_end = False
        if freq_target == 0:
            stop_at_end = True
            freq_target = 1
        step = 1
        if freq_target < freq_start:
            step *= -1
        # self.stepper_step.duty_cycle = 32767
        self.stepper_step.frequency = freq_start
        self.stepper_step.duty_cycle = 65535 // 2
        self.led.duty_cycle = 65535 // 2
        led_freq = int(freq_target // 10)
        if freq_target < 10:
            led_freq = freq_target
            if freq_target == 0:
                led_freq = 2
        self.led.frequency = led_freq
        print(
            "stepper start fade to "
            "{}Hz {:+.2f}RPS  {:+.2f} RPM".format(
                freq_target,
                freq_target/self.freq_steps_factor,
                freq_target/self.freq_steps_factor*60))
        if stop_at_end:
            print("Stop after fade!")

        # delay_time = 0
        # if abs(freq_start - freq_target) > 100000:
        #     delay_time = 0.001
        # for freq in range(freq_start, freq_target, 10):
        for freq in range(freq_start, freq_target, step):
            self.stepper_step.frequency = freq
            self.speed_rps_current = (
                self.stepper_step.frequency / self.freq_steps_factor)
            # print(".", end="")
            # led.frequency = freq // 1000
            if (freq % 100) == 0:
                print(".", end="")
                # print(". {}Hz".format(self.stepper_step.frequency))
            # time.sleep(delay_time)
        print("")
        if stop_at_end:
            self.stop()
        else:
            print(
                "stepper running at "
                "{}Hz {:+.2f}RPS  {:+.2f} RPM".format(
                    self.stepper_step.frequency,
                    self.stepper_step.frequency/self.freq_steps_factor,
                    self.stepper_step.frequency/self.freq_steps_factor*60))
            self.stepper_run = True

    ##########################################
    # state managment

    def run(self, freq=200):
        """Run Stepper Motor with given frequency."""
        self.stepper_step.frequency = freq
        self.stepper_step.duty_cycle = 65535 // 2
        led_freq = freq // 10
        if freq < 10:
            led_freq = freq
        self.led.frequency = led_freq
        self.led.duty_cycle = 65535 // 2
        # self.stepper_step.duty_cycle = 32767
        print("stepper run @{}Hz".format(self.stepper_step.frequency))
        self.stepper_run = True

    def stop(self):
        """Stop Stepper Motor."""
        self.stepper_step.duty_cycle = 0
        self.stepper_step.frequency = 10
        self.led.duty_cycle = 0
        print("stepper stopped.")
        self.stepper_run = False

    def toggle(self):
        """Toggle running state."""
        # print("stepper_run", self.stepper_run)
        self.stepper_run = not self.stepper_run
        # print("stepper_run", self.stepper_run)
        if self.stepper_run:
            # print("fade_to_rps target")
            self.fade_to_rps(self.speed_rps_target)
        else:
            # print("fade_to 0")
            self.fade_to(0)
        # print("stepper_run", self.stepper_run)


    ##########################################
    # common api

    def update(self):
        """Loop."""
        if self.state is self.STATE_STANDBY:
            pass
        elif self.state is self.STATE_FADING:
            pass
        elif self.state is self.STATE_RUNNING:
            pass


##########################################
# main loop
#
# if __name__ == '__main__':
#     # nothing to do
