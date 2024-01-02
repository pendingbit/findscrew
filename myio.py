#!/usr/bin/env python

import RPi.GPIO as GPIO
from threading import Thread
import time

io_event = 0
io_clean = False
iothread = None
# Pin Definitions
input_pin = 18
output_pin = 16     

def io_get_event():
    global io_event

    if io_event==True:
        io_event=False
        return True
    else:
        return False

def io_set_status(status):

    if status == 0:
        GPIO.output(output_pin, GPIO.LOW)
    else:
        GPIO.output(output_pin, GPIO.HIGH)

# Pin Setup:
GPIO.setmode(GPIO.BOARD)  # BCM pin-numbering scheme from Raspberry Pi
# set pin as an output pin with optional initial state of HIGH
GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(input_pin, GPIO.IN)
print("io_init pass")

def io_task():
    global io_event,io_clean
    prev_value = GPIO.HIGH

    try:
        while True:
            value = GPIO.input(input_pin)
            if prev_value==GPIO.HIGH and value==GPIO.LOW:
                #print("io event is true")
                io_event = True
            prev_value = value
            if io_clean:
                break
    finally:
        print("gpio clean up")
        GPIO.cleanup()

def main():
    global iothread
    iothread = Thread(target = io_task)
    iothread.daemon = True
    iothread.start()

if __name__ == '__main__':
    main()
