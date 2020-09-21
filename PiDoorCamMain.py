import PiDoor_Classes
from PiDoor_Classes import FileInfo
from PiDoor_Classes import MCU
from PiDoor_Classes import PROTOCOL
from PiDoor_Classes import UserSettings
import time
from time import sleep
import threading
from PiDoorCam_Classes import COMM
from PiDoorCam_Classes import Stream


BTAddr = 'B8:27:EB:40:69:B8'
ip = '141.215.108.146'
MCU_cam = MCU()
protocol = PROTOCOL("INET")

'''comm = COMM(protocol, BTAddr, 4, 5, 1024)
#comm = COMM(protocol, BTAddr, 4, 5, 1024)
#comm.OpenCOMM_server()
comm.OpenComm()
#t1 = threading.Thread(target = temp)
#t1.start()
comm.Connect()
#comm.COMM_server_accept()
#comm.send_msg_text("TEST")'''


'''Main 12-6 10:30'''
comm = COMM(protocol, ip, 8007, 5, 1024)
try:

    comm.OpenComm()
    streamThread = threading.Thread(target=Stream, ars=())
    streamThread.start()
    print("test")
    while True:
        comm.newhandler()
except KeyboardInterrupt:
    comm.CommClose()
except Exception as e:
    print("error1: {}".format(str(e)))
finally:
    comm.CommClose()

