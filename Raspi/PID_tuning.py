import CANbus
import can

global P_val, I_val, D_val

def get_PID_val():
    P_val = input("P =")
    I_val = input("I =")
    D_val = input("D =")

    P_val = P_val * 10
    I_val = I_val * 10
    D_val = D_val * 100

def send_PID_val(moduleID, P,I,D):
     CANbus.send((moduleID - 0x100), [P, I, D])

