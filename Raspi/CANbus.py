import can
from datetime import datetime

bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=1000000)

class module:
    def __init__(self, ID):
        self.ID = ID
        self.timeout = 0

def send (id, data):
    msg = can.Message(arbitration_id = id, data = data, is_extended_id=False)
    try:
        bus.send(msg)
        print("Message sent on {}".format(bus.channel_info), datetime.now())
        return 1
    except can.CanError:
        #print("Message NOT sent")
        return 0

def receive ():
    try:
        while True:
            msg = bus.recv(0.1)
            #return msg
            if msg is not None:
                return msg

    except KeyboardInterrupt:
        pass  # exit normally

def receiveNonBlocking (to):
    msg = bus.recv(to)
    return msg
