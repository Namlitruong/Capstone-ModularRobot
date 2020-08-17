import csv

#############################--INTERRUPT--######################################
import time
import os, signal 
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def interrupt_handler(channel):
    ID = os.getppid()
    print(ID)
    pid = os.popen("ps aux | grep 'python3 Config.py' | awk '{print $2}'").readlines()
    print ("Length: ", len(pid))        
    for i in range (len(pid)):
        print (pid[i])
        os.system ('sudo kill -9 '+ pid[i])
  

    print("####################################")

GPIO.add_event_detect(13, GPIO.RISING,
                      callback=interrupt_handler,
                      bouncetime=500)
###################################################################################

def detectedModule (data):
    actuatorID = data[0]
    sensorID = data[1]

    for i in range (len(actuatorID)):
        actuatorID[i] = int(actuatorID[i])
    for i in range (len(sensorID)):
        sensorID[i] = int(sensorID[i])
    
    print ( "Number of module found: ")
    print ("Actuator: ", len(actuatorID))
    print ("Sensor: ", len(sensorID))

    return actuatorID, sensorID

def printPos ():
    print ("    ------------------------")
    print ("   / Joint 2/ Joint 3/      \"")
    print (" ------------------- \Joint 4\"")
    print (" / Joint /            --------- ")
    print ("/   1   /             \ \    \ \"")
    print ("-------                \ __\ \__\"")
    print ("| Base |                 Gripper")
    print ("-------")

def setModuleName ():
    printPos ()
    print ("Assign module position: ")
    print ("1. Base")
    print ("2. Joint 1")
    print ("3. Joint 2")
    print ("4. Joint 3")
    print ("5. Joint 4")
    print ("6. Gripper")
    while (True):
        pos = input()
        if (pos == '1'):
            name = str("Base")
            break
        elif (pos == '2'):
            name = str("Joint1")
            break
        elif (pos == '3'):
            name = str("Joint2")
            break
        elif (pos == '4'):
            name = str("Joint3")
            break
        elif (pos == '5'):
            name = str("Joint4")
            break
        elif (pos == '6'):
            name = str("Gripper")
            break
        else:
            print ("Invalid assign")
    
    return name

def assignModule1(str, moduleID, assignID):
    while (True):
        print ("Assign name for module ", str, hex(moduleID[0]))
        name = setModuleName ()
        name = name + "_" + str
        assignID.append ([name, moduleID[0]])
        moduleID.remove (moduleID[0])
        if (len(moduleID) == 0):
            break

def assignModule(str, moduleID, assignID):
    while (True):
        existFlag = False
        print ("Assign name for module ", str, hex(moduleID[0]))
        name = setModuleName ()
        name = name + "_" + str
        for i in range (len(assignID)):
            print ("name ", assignID[i][0])
            if (name == assignID[i][0]):
                existFlag = True
        if (existFlag == False):
            assignID.append ([name, moduleID[0]])
            moduleID.remove (moduleID[0])
            if (len(moduleID) == 0):
                break
        else:
            print ("This part have been occupied. Please choose another one")


if __name__ == "__main__":
    assignID = []
    f = open('config.csv', 'r')
    with f:

        reader = csv.reader(f, delimiter=";")
        data = list(reader) 

    actuatorID, sensorID = detectedModule (data)

    assignModule("Servo", actuatorID, assignID)
    #assignModule("Sensor", sensorID, assignID)

    f = open ('assign.csv', 'w')

    with f:
        writer = csv.writer(f, delimiter = ";")
        for row in range (len(assignID)):
            writer.writerow (assignID[row])



    
