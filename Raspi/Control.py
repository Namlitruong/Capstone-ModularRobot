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
    
    global Base 
    global Joint1, Joint2, Joint3, Joint4 
    global Gripper 

    for i in range (len(data)):
        if (data[i][0] == 'Base_Servo'):
            Base = int (data[i][1])
        elif (data[i][0] == 'Joint1_Servo'):
            Joint1 = int (data[i][1])
        elif (data[i][0] == 'Joint2_Servo'):
            Joint2 = int (data[i][1])
        elif (data[i][0] == 'Joint3_Servo'):
            Joint3 = int (data[i][1])
        elif (data[i][0] == 'Joint4_Servo'):
            Joint4 = int (data[i][1])
        elif (data[i][0] == 'Gripper_Servo'):
            Gripper = int (data[i][1])

def ServoControl (moduleID, angle):
    CANbus.send((moduleID - 0x100), angle)

def confirm ():
    flagBase = flagJoint1 = flagJoint2 = flagJoint3 = flagJoint4 = False
    while (True):

        msg = CANbus.receiveNonBlocking(0.1)

        if (msg == None):
            strID = []
            cTime = datetime.now()
            elapseTime = cTime - sTime
            print (elapseTime)
            if (elapseTime.seconds >= 2):
                print ("ERROR Detected !!!!")
                print ("OPERATION POSTPONE")
                if (flagBase == True ):
                    strID.append (str(Base))
                if (flagJoint1 == True ):
                    strID.append (str(Joint1))
                if (flagJoint2 == True ):
                    strID.append (str(Joint2))
                if (flagJoint3 == True ):
                    strID.append (str(Joint3))
                if (flagJoint4 == True ):
                    strID.append (str(Joint4))
                print ("CACACACA   ",strID)

                f = open ('control.csv', 'w')

                with f:
                    writer = csv.writer(f, delimiter = ";")
                    for row in range (len(strID)):
                        writer.writerow (strID[row])

                return False
        else:
            if (flagBase == False and flagJoint1 == False and flagJoint2 == False and flagJoint3 == False and flagJoint4 == False):
                sTime = datetime.now()

            if (msg.arbitration_id == Base and flagBase == False):
                print ("confirm flagBase", datetime.now(), "ReceiveID:  ", msg.arbitration_id, "BaseID:  ", Base)
                flagBase = True
            if (msg.arbitration_id == Joint1 and flagJoint1 == False):
                print ("confirm flagJoint1", datetime.now(), "ReceiveID:  ", msg.arbitration_id, "Joint1ID:  ", Joint1)
                flagJoint1 = True
            if (msg.arbitration_id == Joint2 and flagJoint2 == False):
                print ("confirm flagJoint1", datetime.now(), "ReceiveID:  ", msg.arbitration_id, "Joint2ID:  ", Joint2)
                flagJoint2 = True
            if (msg.arbitration_id == Joint3 and flagJoint3 == False):
                print ("confirm flagJoint1", datetime.now(), "ReceiveID:  ", msg.arbitration_id, "Joint3ID:  ", Joint3)
                flagJoint3 = True
            if (msg.arbitration_id == Joint4 and flagJoint4 == False):
                print ("confirm flagJoint1", datetime.now(), "ReceiveID:  ", msg.arbitration_id, "Joint4ID:  ", Joint4)
                flagJoint4 = True

            if (flagBase == True and flagJoint1 == True and flagJoint2 == True and flagJoint3 == True and flagJoint4 == True):
                print ("confirm init", datetime.now())
                return True         
            
#############################--GET_SEND_PID--######################################

if __name__ == "__main__":

    setupModule ()
    escapeCondition = True

    while(escapeCondition):
        CANbus.send((Base-0x100), [180])
        CANbus.send((Joint1-0x100), [180])
        CANbus.send((Joint2-0x100), [180])
        CANbus.send((Joint3-0x100), [180])
        CANbus.send((Joint4-0x100), [180])
        confirm ()
        time.sleep(1)
        CANbus.send((Base-0x100), [90])
        CANbus.send((Joint1-0x100), [90])
        CANbus.send((Joint2-0x100), [90])
        CANbus.send((Joint3-0x100), [90])
        CANbus.send((Joint4-0x100), [90])
        escapeCondition = confirm ()
        time.sleep(1)

    print ("Waiting for field engineer !!!")