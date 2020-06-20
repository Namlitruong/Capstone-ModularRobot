import csv
import time
import CANbus
from datetime import datetime
import can

#############################--INTERRUPT--######################################
import time
import os, signal 
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def interrupt_handler(channel):
    print("##############--INTERRUPT--##################")
    motorControl (Lower_BLeft_Actuator, 0x00, 0x00)
    motorControl (Lower_BRight_Actuator, 0x00, 0x00)
    ID = os.getppid()
    print(ID)
    pid = os.popen("ps aux | grep 'python3 Control.py' | awk '{print $2}'").readlines()
    print ("Length: ", len(pid))        
    for i in range (len(pid)):
        print (pid[i])
        os.system ('sudo kill -9 '+ pid[i])
        print("KILL " , i)


GPIO.add_event_detect(13, GPIO.RISING,
                      callback=interrupt_handler,
                      bouncetime=500)
###################################################################################

def setupModule ():
    f = open('assign.csv', 'r')
    with f:

        reader = csv.reader(f, delimiter=";")
        data = list(reader) 
    
    global Lower_BLeft_Actuator 
    global Lower_BRight_Actuator 
    global Lower_Center_Sensor 

    for i in range (len(data)):
        if (data[i][0] == 'Lower_BLeft_Actuator'):
            Lower_BLeft_Actuator = int (data[i][1])
        elif (data[i][0] == 'Lower_BRight_Actuator'):
            Lower_BRight_Actuator = int (data[i][1])
        elif (data[i][0] == 'Lower_Center_Sensor'):
            Lower_Center_Sensor = int (data[i][1])

def motorControl (moduleID, dir, pwm):
    CANbus.send((moduleID - 0x100), [dir, pwm])

def confirm (ID1, ID2):
    flag1 = flag2 = False
    while (True):

        msg = CANbus.receive()
        
        if (msg.arbitration_id == ID1 and flag1 == False):
            print ("confirm flag1", datetime.now())
            flag1 = True
        if (msg.arbitration_id == ID2 and flag2 == False):
            print ("confirm flag2", datetime.now())
            flag2 = True
        if (flag1 == True and flag2 == True):
            print ("confirm init", datetime.now())
            return True

if __name__ == "__main__":

    setupModule ()


    while (True):
        motorControl (Lower_BLeft_Actuator, 0xaa, 200)
        motorControl (Lower_BRight_Actuator, 0xaa, 200)
        confirm (Lower_BLeft_Actuator, Lower_BRight_Actuator)
        print ("#1" , datetime.now())
        time.sleep (2)
        
        motorControl (Lower_BLeft_Actuator, 0xbb, 200)
        motorControl (Lower_BRight_Actuator, 0xbb, 200)
        confirm (Lower_BLeft_Actuator, Lower_BRight_Actuator)
        print ("#2", datetime.now())
        time.sleep (2)
        
        motorControl (Lower_BLeft_Actuator, 0xbb, 200)
        motorControl (Lower_BRight_Actuator, 0xaa, 200)
        confirm (Lower_BLeft_Actuator, Lower_BRight_Actuator)
        print ("#3", datetime.now())
        time.sleep (2)

        
        motorControl (Lower_BLeft_Actuator, 0xaa, 200)
        motorControl (Lower_BRight_Actuator, 0xbb, 200)
        confirm (Lower_BLeft_Actuator, Lower_BRight_Actuator)
        print ("#4", datetime.now())
        time.sleep (2)
        
        motorControl (Lower_BLeft_Actuator, 0x00, 200)
        motorControl (Lower_BRight_Actuator, 0x00, 200)
        confirm (Lower_BLeft_Actuator, Lower_BRight_Actuator)
        print ("#5", datetime.now())
        time.sleep (2)

    