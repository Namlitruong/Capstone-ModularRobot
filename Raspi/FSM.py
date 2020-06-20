

import RPi.GPIO as GPIO
import os
import time

state = -1

Forward = 26
Backward = 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

os.system ("pwd")

print ("Forward to START")

def interrupt_handler(channel):
    global state

    print("State change")

    if channel == Forward:
        if state == -1:
            print("######--CONFIRM STATE--######")
            state = 0
            os.system("sudo python3 Confirm.py")
            print("######--EoS--######")
            
        elif state == 0:
            print("######--CONFIG STATE--######")
            state = 1 
            os.system("sudo python3 Config.py")
            print("Config Done - Forward to Control")
            print("######--EoS--######")
            
        elif state == 1:
            print("######--CONTROL STATE--######")
            state = 2
            os.system("sudo python3 Control.py")
            print("######--EoS--######")

        elif state == 2:
            print("######--CONFIRM STATE--######")
            state = 0 
            os.system("sudo python3 Confirm.py")
            print("######--EoS--######")
            

    
    elif channel == Backward:
        if state == 1:
            print("######--CONFIRM STATE--######")
            state = 0
            os.system("sudo python3 Confirm.py")
            print("######--EoS--######")
            
            
        elif state == 2:
            print("######--CONFIG STATE--######")
            state = 1 
            os.system("sudo python3 Config.py")
            print("######--EoS--######")
            
            

GPIO.add_event_detect(26, GPIO.RISING,
                      callback=interrupt_handler,
                      bouncetime=500)

GPIO.add_event_detect(19, GPIO.RISING,
                      callback=interrupt_handler,
                      bouncetime=500)


try:
    while (True):
        time.sleep(0)
except KeyboardInterrupt:
    raise

