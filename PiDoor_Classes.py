'''*************************************
    PiDoor_Classes
    Shared classes between all PiDoor MCUs
*************************************'''

'''------------------------------------
FileInfo class: Used to implement file properties
    throughout the program
-------------------------------------'''

import os
from os import path
import socket
import pickle
import logging
import time
import os
import struct ## new
import threading


COMM_ERROR_RECV_MSG_TEXT = "Error in receiving text over COMM"
COMM_ERROR_RECV_MSG_PICKLE = "Errpr om receivomg pickle object over COMM"
COMM_ERROR_CONN_CLOSED = "Error. Connection not open"

COMM_CONN_VERIFY = "CONN Verified"

COMM_ACTION_BELLRUNG = 1
COMM_ACTION_THROW_MD_PICS = 2
COMM_ACTION_NEW_SETTINGS = 3

COMM_RECV_TEXT_TIMEOUT = 15
COMM_RECV_PICKLE_TIMEOUT = 30
COMM_RECV_IMAGE_TIMEOUT = 300

MSG_TYPE_PICKLE = "P"
MSG_TYPE_T = "T"
MSG_TYPE_I = "I"

MSG_RQST_SEND_FILENAME = "send name"

HEADER_SIZE = 15



DB_IMAGE_FILEPATH = "/home/pi/Documents/PiDoor/bell_rung_images/"
MD_IMAGE_FILEPATH = "/home/pi/Documents/PiDoor/motion_detect_images/"

PN_DB_RUNG_MSG = "Hello! Some one is at your door. To view Live Feed, click link below"

class MsgTemplate:
    def __init__(self, mtype = None, msg = None):
        self.mtype = mtype
        self.msg = msg
        if msg:
            self.len = len(msg)

    def getoutmsg(self):
        sheader = '{:<15}'.format("{}:{}".format(self.mtype, self.len)) + self.msg
        return sheader
    
    def parsemsg(self, inmsg):
        self.msg = inmsg[15:]
        temp = inmsg[:15].split(':')
        self.mtype = temp[0]
        self.len = int(temp[1])
        
class FileInfo:
    def __init__(self, fileName, fullPath, parentDirectory, fileType):
        self.fileName = fileName
        self.fullPath = fullPath
        self.parentDirectory = parentDirectory
        self.fileType = fileType
        
    
    def __init__(self, fullPath):
        self.fileName = os.path.basename(fullPath) 
        self.fullPath = os.path.realpath(fullPath)
        self.parentDirectory = os.path.dirname(fullPath)
        self.fileType = os.path.splitext(fullPath)[1]
    
    
        
class MCU(object):
    def __init__(self, IPaddr= None, MAC = None, BDaddr = None):
        self.IP_address = IPaddr
        self.Mac_address = MAC
        self.BD_address = BDaddr

class PROTOCOL(object):
    def __init__(self, mode):
        if(mode == "BT"):
            self.AF = socket.AF_BLUETOOTH
            self.STREAM = socket.SOCK_STREAM
            self.PROTO = socket.BTPROTO_RFCOMM
        elif(mode == "INET"):
            self.AF = socket.AF_INET
            self.STREAM = socket.SOCK_STREAM
            self.PROTO = None
            
        else:
            print("Not an acceptable protocol")
        
'''------------------------------------
UserSettings class: Used to store all user setting

-------------------------------------'''

class UserSettings(object):
    def __init__(self, MCU_Chime = None, MCU_Cam = None, DNE_start = None, DNE_stop = None, defaultChime = None,
                 randomChimeEnable = None, audioFilesPath = None, detectionDistance = None):
        
        self.MCU_Chime = MCU_Chime
        
        self.MCU_Cam = MCU_Cam
        
        self.DNE_start = DNE_start
        self.DNE_stop = DNE_stop
        self.defaultChime = defaultChime
        
        self.randomChimeEnable = randomChimeEnable
        
        self.audioFilesPath = audioFilesPath
        
        #Will setup later
        self.detectionDistance = detectionDistance
    
        
class COMM(object):
    def __init__(self):
        self.COMM_open = False
        self.server_socket = None
        self.serverMACAddress = serverMACAddress
        self.port = port
        self.backlog = backlog
        self.buff_size = buff_size
        
    def __init__(self, protocol, bindAddr, port, backlog = 3, buff_size= 1024):
        self.protocol = protocol
        self.COMM_open = False
        self.bindAddr = bindAddr
        self.port = port
        self.backlog = backlog
        self.buff_size = buff_size
        self.server_socket = None

    def OpenCOMM_server(self):   
        try:
            self.server_socket = socket.socket(self.protocol.AF, self.protocol.STREAM, self.protocol.PROTO)
            self.server_socket.settimeout(None)
            self.server_socket.bind((self.bindAddr, self.port))
            self.server_socket.listen(self.backlog)
            
            while (self.COMM_open):
                try:
                    client, address = s.accept()
                    print("New Connectoin at {}".format(address))
                except:
                    print("Error on open inner try connection")
                    time.sleep(3)
                    
        except:
            print("error on open outer try")
            
    def COMM_server_accept(self):
        if not (self.COMM_accept):
            self.COMM_accept = True
            
        while(self.COMM_accept):
            try:
                self.client, self.address = self.server_socket.accept()
                print("New Connectoin at {}".format(address))
                self.new_CONN = True
                self.server_handler()
            except KeyboardInterrupt:
                self.server_socket.close()
                
    def COMM_server_handler(self):
        if (self.new_CONN):
            self.send_msg_text(COMM_CONN_VERIFY)
            data = self.client.recv(self.buff_size)
            print(data)
        else:
            print("TODO")
        
    def OpenCOMM_client(self):
        self.server_socket  = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

        self.server_socket.connect((self.bindAddr, self.port))
        self.server_socket.setblocking(False)
        print(self.bindAddr)

        try:
            #self.server_socket = socket.socket(self.protocol.AF, self.protocol.STREAM, self.protocol.PROTO)
            
            #self.server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            #self.server_socket.connect((self., self.port))
            self.COMM_open = True
            msg_in = self.recv_msg_text()
            print(msg_in)
            if (msg_in == COMM_CONN_VERIFY):
                print("Here")
                time.sleep(.1)
                #c= input("input: ")
                print("before call out text method")
                print(COMM_CONN_VERIFY)
                self.send_msg_text(COMM_CONN_VERIFY)    
                print("after call out text method")
            else:     
                #throw error with error string
               print("Open client message not same")
               self.COMM_open = False
                
        except:
            self.COMM_open = False
            print("error on outer open client")

            
    def OpenCOMM_Test(self):
        self.server_socket  = socket.socket(self.protocol.AF, socket.SOCK_STREAM)
        #self.server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.server_socket.connect((self.bindAddr, self.port))
        self.server_socket.setblocking(False)
        print(self.bindAddr)
        
        self.COMM_open = True

        
    def OpenCOMM(self, serverMACAddress, port, backlog = 5, buff_size = 30):
        self.serverMACAddress = serverMACAddress
        self.port = port
        self.backlog = backlog
        self.buff_size = buff_size
        
        try:
            self.server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.server_socket.connect((self.serverMACAddress, self.port))
            
            msg_in = self.recv_msg_text()
            if (msg_in == COMM_CONN_VERIFY):
                    
                self.COMM_open = True
            else:     
                #throw error with error string
               print("error")
                
        except:
            self.COMM_open = False
        
        
    
    def CloseCOMM(self):
        try:
            self.server_socket.close()
            self.COMM_open = False
        except:
            print("error closing")

    def recv_msgHandler(self, msgAttr):
        if(msgAttr.mtype == MSG_TYPE_T):
            msgAttr.msg = msgAttr.msg.decode("utf-8")
                
        elif(msgAttr.mtype == MSG_TYPE_P):
            msgAttr.msg = pickle.loads(msgAttr.msg)

        elif(msgATTR.mtype == MSG_TYPE_I):
            msgAttr.msg = MsgAttr.msg
        else:
             return("error. RECV type not found")
            
    def send_msg_pickle(self, obj):
        if(self.COMM_open):
            try:
                msg = pickle.dumps(obj)
                mTemp = MsgTemplate(MSG_TYPE_P, msg)
                print("message length: {}".format(mTemp.len))
                print(msg)
                self.server_socket.send(mTemp.getoutmsg())
            except Exception as e:
                print("error [pickle: {}".format(str(e)))
            except:
                print("Error sending pickle")
        else:
            print("Error COMM not open")
            
    def send_msg_text(self, msg):
        if(self.COMM_open):
            #do something
            print("COMM Open in send msg")
            try:
                print("Trying to send: {}".format(msg.encode("utf-8")))
                print("should send as {}".format(bytes(msg, "UTF-8")))
                '''print(MSG_TYPE_T)
                mTemp = MsgTemplate(MSG_TYPE_T, msg)
                print(mTemp.getoutmsg())
                self.server_socket.send(mTemp.getoutmsg().decode("utf-8"))'''
                self.server_socket.send(bytes(msg,"utf-8"))
                print("sent message")
            except:
                #throw error
                print("error sending")
                mError = "something"
        else:
            #throw error
            print("error")
            
    def recv_msg(self):
        msgData = b''
        try:
            temp = self.server_socket.recv(self.buff_size)
            temp = temp.decode("utf-8")
            if not len(temp):
                return False
            msgAttr = MsgTemplate()
            msgAttr.parsemsg(temp)
            while True:
                if (len(msgAttr.msg) - HEADER_SIZE == msgAttr.len):
                    return(msgATTR)
                temp = self.server_socket.recv(self.buff_size)
                if not len(msg):
                    return("error")
                msgATTR.msg += MsgTemplate().parsemsg(temp).msg
        except:
            return(False)
            
        
    def recv_msg_text(self):
        if(self.COMM_open):
            
            
            temp = self.server_socket.recv(self.buff_size)
            print(temp)
            #temp = temp.decode("utf-8")
            try:
                temp = temp.decode("utf-8")
                return(temp)
            except:
                print("something")
                return(COMM_ERROR_RECV_MSG_TEXT)
                    
        else:
            print(COMM_ERROR_CONN_CLOSED)
            return(COMM_ERROR_CONN_CLOSED)

    def recv_image_handler(self):
        self.send_msg_text(MSG_RQST_SEND_FILENAME)
        fileName = self.recv_msg_text()

        new_img = create_new_file(fileName, DB_IMAGE_FILEPATH)
        time.sleep(1)
        imgData = self.recv_msg_IMGP()
        nIMG = open(new_img.fullPath, "wb")
        nIMG.write(imgData)
        nIMG.close()
        return(new_img)
        
    def recv_msg_IMGP(self):
        data = b''
        payload_size = struct.calcsize(">L")
        print("payload size: {}".format(payload_size))
        while True:
            try:
                while len(data) < payload_size:
                    print("Recv: {}".format(len(data)))
                    data += self.server_socket.recv(4096)

                print("Done Recv: {}".format(len(data)))
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L", packed_msg_size)[0]
                print("msg_size: {}".format(msg_size))
                while len(data) < msg_size:
                    data += self.server_socket.recv(4096)
                frame_data = data[:msg_size]
                data = data[msg_size:]
                img = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                return (img)
            except Exception as e:
                print("erroerr: {}".format(str(e)))            
    
            
    def recv_msg_pickle(self):
        if(self.COMM_open):
            while True:
                temp = self.server_socket.recv(self.buff_size)
                try:
                    return(pickle.loads(temp))
                except Exception as e:
                    print("Pickle Error: {}".format(str(e)))
                except:
                    return(COMM_ERROR_RECV_MSG_PICKLE)
        else:
            print(COMM_ERROR_CONN_CLOSED)
            return(COMM_ERROR_CONN_CLOSED)
            
    def recv_msg_Img(self):
        if(self.COMM_open):
            print("hello")
            i = 1
            temp_newImgPath = "./"
            temp_newImgName = "temp.jpg"
            nfileInfo = None
            fData = b''
            while i == 1:
                msg = self.server_socket.recv(self.buff_size)
                print("in while")
                try:
                    decoded_msg = msg.decode("utf-8")
                    print(decoded_msg)
                    #maybe add pickle object here
                    if decoded_msg.startswith('start'):
                        print("if it starts start")
                        #nfileInfo = create_new_file(temp_newImgName, newImgPath)
                        nFile = open("/home/pi/Documents/PiDoor/test.jpg", "wb")
                        nFile.close()
                        nfileInfo = FileInfo("/home/pi/Documents/PiDoor/test.jpg")
                        #creaed fileInfo
                        temp = full_msg.split()
                        
                        self.buff_size = int(temp[1])
                        print(buff_size)
                    #time.sleep(1)
                    elif decoded_msg == "stop":
                        self.buff_size = 1024
                        print("stop command")
                        i = 0
                        cFile = open(nFileInfo.fullPath, 'wb+')
                        cFile.write(fData)
                        cFile.close()
                        
                        break
                    else:
                        '''print("here")
                        cFile = open(newFilePath, 'wb+')
                        cFile.write(msg)
                        cFile.close()'''
                except:
                    '''fData =  msg
                    print(fData)
                    time.sleep(1)
                    cFile = open(newFilePath, 'wb+')
                    cFile.write(fData)
                    cFile.close()
                    print("Error")'''
                    fData = fData + msg
                    print("recieved {} of {}".format(len(fData), self.buff_size))
                    #time.sleep(1)
                time.sleep(.2)
                
        else:
             print("Throw error")


def create_new_file(fileName, filePath):
    nFile = open(os.path.join(filePath, fileName), 'wb')
     
    nFile.close()
    return(FileInfo(os.path.join(filePath, fileName)))

def create_new_file_ext(fileName, ext, filePath):
    nFile = open(os.path.join(filePath, "{}{}".format(fileName, ext)), 'wb')
     
    nFile.close()
    return(FileInfo(os.path.join(filePath, fileName)))
