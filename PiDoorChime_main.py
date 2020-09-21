import sys
import os
import PiDoor_Classes as PiDoor
from PiDoor_Classes import PROTOCOL
from PiDoor_Classes import MCU
from PiDoor_Classes import UserSettings
from PiDoor_Classes import COMM
from PiDoor_Classes import FileInfo
import PiDoorChime_Classes as PiDoorChime
from PiDoorChime_Classes import FileObjs
from PiDoorChime_Classes import PushoverSender
from PiDoorChime_Classes import Door_Btn
import random
import time
import errno


#False is unlocked
#True is Locked
mutex_lock = False

def frontDoorHandler(pin):
    if not mutex_lock:
        mutex_lock = True
        print("Handling handler")
        fHRunning = False
        try:
            INET.OpenCOMM_Test()
            fHRunning = True
        except Exception as e:
            print("Error trying to connect {}".format(str(e)))
            if str(e) == errno.ECONNREFUSED:
                print("Connection can't open")
                
        audioFileInfo = audioFiles.files[random.randint(0, len(audioFiles.files))-1]
        PiDoorChime.play_mp3(audioFileInfo)
        if fHRunning:
            try:
                nFileInfo = INET.recv_image_handler()
                time.sleep(5)
                pushNotify.send_img_notification(PiDoor.PN_DB_RUNG_MSG, nFileInfo)
            
                time.sleep(3)
                print("Going to close")
                INET.CloseCOMM()
            except Exception as e:
                print("Exception in btn handler 1: {}".format(str(e)))
        else:
            try:
                print("Jere")
                pushNotify.send_txt_notification(PiDoor.PN_DB_RUNG_NO_CAM_MSG)
            except Exception as e:
                print("Exception in btn handler 1: {}".format(str(e)))
        time.sleep(3)
        fHRunning = False
    mutex_lock = False


#Initialization 
PO_USER_KEY = "unap6iwqf999bss3xt2imvoptc1qms"
PO_API_KEY = "abqwsnmuqwjf8oxjkpa4oomoeeuppp"
audioFiles = FileObjs("/home/pi/Documents/Audio_Files/", ".mp3")
audioFiles.setFiles("/home/pi/Documents/Audio_Files/")   
mcu_chime = MCU()

mcu_cam = MCU(IPaddr=None, MAC = None, BDaddr = 'b8:27:eb:40:69:b8')
settings = UserSettings(mcu_chime, mcu_cam, None, None, None, None, None, None)
INET_protocol = PROTOCOL("INET")
INET = COMM(INET_protocol, '141.215.108.146', 8007)


frontDoorBTN = Door_Btn( 23, frontDoorHandler)
pushNotify = PushoverSender(PO_USER_KEY, PO_API_KEY)

frontDoorBTN.startDetection()
while True:
    try:
        time.sleep(15)
        print("waititit")
    except KeyboardInterrupt:
        
        frontDoorBTN.Cleanup()
    except Exception as e:
        print("Main Error: ".format(str(e)))
        
frontDoorBTN.Cleanup()             

