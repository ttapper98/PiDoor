'''*************************************
    PiDoorChime
    Classes used by PiDoor chime box
*************************************'''

import PiDoor_Classes as PiDoor_shared
from PiDoor_Classes import FileInfo
from PiDoor_Classes import MCU
from PiDoor_Classes import UserSettings
import RPi.GPIO as GPIO
import http.client
import urllib
import os
from os import listdir

import requests
import time
import subprocess


#mUserKey = "unap6iwqf999bss3xt2imvoptc1qms"
#mAPIKey = "abqwsnmuqwjf8oxjkpa4oomoeeuppp"


def play_mp3(fileInfo):

    subprocess.Popen(['omxplayer', '-o', 'alsa', fileInfo.fullPath])


class FileObjs(object):
    def __init__(self, dir_path = None, file_extension = None, files = None):
        self.dir_path = dir_path
        self.file_extension = file_extension
        self.files = files
    
    def setFiles(self, dirPath):
        self.files = []
        temp_file_list = [f for f in listdir(self.dir_path) if os.path.isfile(os.path.join(self.dir_path, f)) and f.endswith(self.file_extension)]
        for i in range(len(temp_file_list)):
            self.files.append(1)
            print(self.dir_path)
            print(temp_file_list)
            print(os.path.abspath(temp_file_list[i]))
            print(os.path.realpath(temp_file_list[i]))
            self.files[i] = FileInfo(os.path.join(self.dir_path, temp_file_list[i])) 
        
        #this would work too.
        #temp_file_paths = [f for f in listdir('.') if os.path.isfile(os.path.join('.', f)) and f.endswith(self.fileTypes)]
        
class PushoverSender:
    url_img = "https://api.pushover.net/1/messages.json"
    def __init__(self, user_key, api_key):
        self.user_key = user_key
        self.api_key = api_key
    def send_notification(self, text):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        post_data = {'user': self.user_key, 'token': self.api_key, 'message': text}
        conn.request("POST", "/1/messages.json", urllib.parse.urlencode(post_data), {"Content-type": "application/x-www-form-urlencoded"})
    def send_img_notification(self, msg, file):
        r = requests.post(self.url_img, data = {
            "token": self.api_key ,
            "user": self.user_key,
            "message": msg
            }, files = {
                "attachment": (file.fileName, open(file.fullPath, "rb"), "image/jpeg")
                })
        print(r.text)
        
    def send_txt_notification(self, msg):
        r = requests.post(self.url_img, data = {
            "token": self.api_key ,
            "user": self.user_key,
            "message": msg
            })
        print(r.text)                         

class Door_Btn(object):
    def __init__(self, BCM_pin, handler = None):
        self.BCM_pin = BCM_pin
        GPIO.setmode(GPIO.BCM)
        self.handler = handler
        GPIO.setup(self.BCM_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP )
        self.handler = handler
        self.event_enabled = False
        
    
    def startDetection(self):
        if(self.handler):
            self.add_event_detect()
                
        else:
            print("Throw error, handler does not exist.")
            
    def stopDetection(self):
        self.remove_event_detect()
        
    def add_event_detect(self):
        if not (self.event_enabled):
            try:
                GPIO.add_event_detect(self.BCM_pin, GPIO.RISING, self.BtnHandler, bouncetime=11100)
                #GPIO.add_event_callback(self.BCM_pin, self.BtnHandler)
                self.event_enabled = True
            except Exception as e:
                print("DB add Call back err: {}".format(str(e)))
                
            except:
                print("Throw error, error adding callback")
                
        else:
            print("Error, event already enabled")
    def remove_event_detect(self):
        if(self.event_enabled):
            try:
                GPIO.remove_event_detect(self.BCM_pin)
                self.event_enabled = False
            except:
                print("throw error, error disabling callback")
        else:
            print("Error, event not enabled")
            
    def BtnHandler(self, pin):
        #setup later"
        self.remove_event_detect()
        self.handler(pin)
        
        self.add_event_detect()

    def Cleanup(self):
        try:
            GPIO.cleanup()
            print("GPIOs have been cleaned up")
        except:
            print("already cleaned up")
        
