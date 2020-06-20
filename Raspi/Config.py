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
    print ("--------------------------")
    print ("|   TLeft       TRight   |")
    print ("|                        |")
    print ("|         Center         |")
    print ("|                        |")
    print ("|   BLeft       BRight   |")
    print ("--------------------------")

def setModuleName ():
    print ("Choose the side: ")
    print ("1. Upper")
    print ("2. Lower")
    while (True):
        side = input()
        if (side == '1'):
            name = "Upper"
            break
        elif (side == '2'):
            name = "Lower"
            break
        else:
            print ("Invalid assign")

    printPos ()
    print ("Assign module position: ")
    print ("1. TLeft")
    print ("2. TRight")
    print ("3. Center")
    print ("4. BLeft")
    print ("5. BRight")
    while (True):
        pos = input()
        if (pos == '1'):
            name = name + str("_TLeft")
            break
        elif (pos == '2'):
            name = name + str("_TRight")
            break
        elif (pos == '3'):
            name = name + str("_Center")
            break
        elif (pos == '4'):
            name = name + str("_BLeft")
            break
        elif (pos == '5'):
            name = name + str("_BRight")
            break
        else:
            print ("Invalid assign")
    
    return name

def assignModule(str, moduleID, assignID):
    while (True):
        print ("Assign name for module ", str, hex(moduleID[0]))
        name = setModuleName ()
        name = name + "_" + str
        assignID.append ([name, moduleID[0]])
        moduleID.remove (moduleID[0])
        if (len(moduleID) == 0):
            break

    


if __name__ == "__main__":
    assignID = []
    f = open('config.csv', 'r')
    with f:

        reader = csv.reader(f, delimiter=";")
        data = list(reader) 

    actuatorID, sensorID = detectedModule (data)

    assignModule("Actuator", actuatorID, assignID)
    assignModule("Sensor", sensorID, assignID)

    f = open ('assign.csv', 'w')

    with f:
        writer = csv.writer(f, delimiter = ";")
        for row in range (len(assignID)):
            writer.writerow (assignID[row])



    
