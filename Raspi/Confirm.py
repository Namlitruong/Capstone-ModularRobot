import CANbus
import can
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
    pid = os.popen("ps aux | grep 'python3 Confirm.py' | awk '{print $2}'").readlines()
    print ("Length: ", len(pid))        
    for i in range (len(pid)):
        print (pid[i])
        os.system ('sudo kill -9 '+ pid[i])
  

    print("####################################")

GPIO.add_event_detect(13, GPIO.RISING,
                      callback=interrupt_handler,
                      bouncetime=500)
###################################################################################

actuatorID = []
sensorID = []




def wriToFile (aID, sID):
    f = open ('config.csv', 'w')

    with f:
        writer = csv.writer(f, delimiter = ";")
        writer.writerow (aID)
        writer.writerow (sID)

def classifier (msg):
    subID = 0
    mType = 0
    if (msg.arbitration_id == 0x1A0):
        print ("Module detected !!!")
        subID = 0x1A0
        mType = 'A'
    elif (msg.arbitration_id == 0x1F0):
        #print ("Sensor module detected !!!")
        subID = 0x1F0
        mType = 'S'
    return subID, mType

def searchValidID (IDlist, tempModule):
    for i in range (1, 16):
        flag = False
        tempModule.ID = tempModule.ID + 1
        if (len(IDlist) == 0):
            break
        
        for j in range (len(IDlist)):
            
            if (IDlist[j].ID == tempModule.ID):
                flag = True
                break
        if (flag == False and j+1 == len(IDlist)):
            break

    IDlist.append (tempModule)
    print ("Assign new ID: ", hex(tempModule.ID))

    return tempModule.ID

def verifyID (IDlist):
    activeList = []
    for i in range (len(IDlist)):
        while (True):
            CANbus.send((IDlist[i].ID - 0x100), [0x00])
            msg = CANbus.receiveNonBlocking(0.1)
            if (IDlist[i].timeout == 5):
                break
            if (msg == None):
                IDlist[i].timeout = IDlist[i].timeout + 1
            else:
                activeList.append (IDlist[i])
                break
    return activeList

def printAvailableID (msg, module):
    IDlist =[]
    print (msg)
    for i in range (len(module)):
        print (module[i].ID, "   ", i)
        IDlist.append (module[i].ID)
    return IDlist
    
if __name__ == "__main__":
    while (True):
        while (True):
            print ("Waiting for connecting modules")
            msg = CANbus.receive()
            tempID, mType = classifier (msg)
            if (msg.arbitration_id == tempID):
                break

        tempModule = CANbus.module(msg.arbitration_id)

        if (mType == 'A'):
            tempID = searchValidID (actuatorID, tempModule)
            CANbus.send (0x0A0, [(tempID - 0x1A0)])
        elif (mType == 'S'):
            tempID = searchValidID (sensorID, tempModule)
            CANbus.send (0x0F0, [(tempID - 0x1F0)])

        #CANbus.send (0x0A0, [(tempID - 0x1A0)])
        print ("Sending Confirmation", tempID - 0x100)

        while (True):
            msg = CANbus.receive()
            if (msg.arbitration_id == tempID):
                break

        print ("Confirmation Complete")

        #Verify modules
        print ("Verifying existing modules")
        actuatorID = verifyID (actuatorID)
        sensorID = verifyID (sensorID)

        aID = printAvailableID ("Available Module: ", actuatorID)
        #sID = printAvailableID ("Available Sensor: ", sensorID)
        sID = printAvailableID (" ", sensorID)
        wriToFile (aID, sID)