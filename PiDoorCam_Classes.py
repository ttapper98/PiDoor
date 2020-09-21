    
import socket
import picamera
from picamera import PiCamera
import time
import sys
import os
from os import listdir
import io
import logging
import socketserver
from threading import Condition
from http import server
import PiDoor_Classes as PiDoor
from PiDoor_Classes import UserSettings
from PiDoor_Classes import FileInfo
import pickle
import select
import struct
from datetime import datetime
import subprocess
from subprocess import Popen

#import dummy

DB_IMG_FILEPATH = '/home/pi/Documents/'
REPO_IMG_FILEPATH = '/home/pi/Documents/473 Project/PiDoorImg'

'''*************************************
import
PiDoorCam classes

**************************************'''
def templatefname(dtime, imgtype):
    if(imgtype == "db"):
        itype = "DB_"
    else:
        itype = "MD_"
    tempname = itype + dtime.strftime('%_m_%d_%_y_%H.%M')+".jpg"
    return(tempname)
    
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
        self.len = temp[1]
        
    
class PiDoorCam:
    def __init__(self, itype):
        self.itype = itype
        #self.filePath
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.annotate_text_size = 25
        self.camera.annotate_background = picamera.Color('black')
        #self.camera.annotate_text = dtime.strftime('%a %-m/%d/%-y %H:%M')

    def takePicture(self):
        try:
            dtime = datetime.now()
            filename = templatefname(dtime, self.itype)
            print(self.itype)
            self.camera.annotate_text = dtime.strftime('%a %-m/%d/%-y %H:%M')
            print(filename)
            if(self.itype == "db"):
                filepath = DB_IMG_FILEPATH + filename
            elif(self.itype == "md"):
                filepath = REPO_IMG_FILEPATH + filename
            print("start taking pic")
            #self.camera.capture(filepath)
            self.camera.capture(filepath, use_video_port=True)
            print("picture taken")
            self.camera.close()
            print("cam closed")
            return (PiDoor.FileInfo(filepath))
        except Exception as e:
            print("error take picture: {}".format(str(e)))

class COMM:
    def __init__(self, protocol, hostMACaddress, port, backlog = 5, bufsize = 1024):
        self.hostMACaddress = hostMACaddress
        self.port = port
        self.backlog = backlog
        self.buff_size = bufsize
        self.protocol = protocol
        self.CommOpen = False
        self.server_socket =None
        self.client = None
        self.handlerrunning = False
        self.addr = None
        self.NewConn = True
        #os.system("piStream.py")

    def OpenComm(self):
        print("hey")
        self.s = socket.socket(self.protocol.AF, self.protocol.STREAM)
        #self.s.settimeout(0.0)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.hostMACaddress, self.port))
        self.socketlist = [self.s]
        self.s.listen(self.backlog)
        
        print("listening")
        

    def filepather(self, requesttype):
        if(requesttype == 0):
                return(0)
        elif(requesttype == 1):
            
            return(1)
        

    def msghandler(self, request):
        if(self.handlerrunning == False):
            self.handlerrunning = True
            try:
                #if(request == PiDoor.MSG_RQST_DOOR_RUNG):
                    #temp = self.newrecv(self.client)
                print("in message handler")
                print("{}:::{}".format(PiDoor.MSG_RQST_SEND_FILENAME, request))
                    #nextrequest = temp.decode("utf-8")
                if(request == PiDoor.MSG_RQST_SEND_FILENAME):
                    print("cam hereeeeee")
                    camera = PiDoorCam("db")
                    print("taking picture now")
                    self.client.send(bytes("test.jpg", "utf-8"))
                    
                    mfileinfo = camera.takePicture()
                    print(mfileinfo.fullPath)
                    sendImgThread = threading.Thread(target=self.sendimg, args=(mfileinfo))
                    sendImgThread.start()
                    #self.sendimg(mfileinfo)
                    #msg = self.newrecv(self.client)
                    #print(msg)
                    time.sleep(2)
                    
                    fileobjects = FileObjs("/home/pi/Documents/473 Project/Project files/", ".jpg")
                    fileobjects.setFiles("/home/pi/Documents/473 Project/Project files/")

                    for i in range(len(fileobjects.files), 0):
                        x = fileobjects.files[i]
                        y = fileobjects.files[i+1]
                        fielobjects.files[i+1] = fileobjects.files[i]
                    fileopen = open(fileobjects.files[0].fullPath, 'wb')
                    tempf = open(mfileinfo.fullPath, 'rb')
                    tempdata = tempf.read()
                    fileopen.write(tempdata)
                    tempf.close()
                    fileopen.close()
                    
                    #self.client.send(bytes(mfileinfo.fileName, "utf-8"))
            except Exception as e:
                print("erro msg handlerr: {}".format(str(e)))
            self.handlerrunning = False
            
    def sendimg(self, fileinfo):
        print("sending img")
        try:
            while True:
                sFile = open(fileinfo.fullPath, 'rb')
                b = sFile.read()
                fileSize = len(b)
                data = pickle.dumps(b,0)
                print("{}:{}".format(fileSize, len(data)))
                time.sleep(2)
                self.client.sendall(struct.pack(">L", len(data))+data)
                time.sleep(2)

                sFile.close()
                break
        except Exception as e:
            print("error sendimg: {}".format(str(e)))
        
        
    def newhandler(self):
        readsock, _, esock = select.select(self.socketlist, {}, self.socketlist)
        print(readsock)
        for nsocket in readsock:
            if nsocket == self.s:
    
                print("New Connection from {} at {}".format(self.client, self.addr))
                print("here in nsock")
                self.client, self.addr = self.s.accept()
                print(self.addr)
                msg = self.newrecv(self.client)
                print(msg)
                if msg is False:
                    continue
                #temp = self.newrecv(self.client)
                request = msg.decode("utf-8")
                print("request: {}".format(request))
                self.msghandler(request)
                #self.socketlist.append(self.client)
                
            else:
                print("here in else")
                msg = self.newrecv(nsocket)
                if msg is False:
                    print("Closed Connection from {} at {}".format(self.client, self.addr))
                    self.socketlist.remove(nsocket)
                    #self.p = subprocess.call('piStream.py', shell = True)
                    #subprocess.call('dummy.py')
                    continue
                else:
                    print("msg received: {}".format(msg.decode("utf-8")))

    def ConnClientClose(self):
        try:
            self.client.close()
            self.client = None
            self.addr = None
            self.NewConn = True
        except:
            print("Client already closed")

    def CommClose(self):
        self.ConnClientClose()
        try:
            self.s.close()
        except:
            print("failed to close server")

    def send_msg_pickle(self, obj):
        try:
            msg = pickle.dumps(obj)
            self.client.send(msg)
        except Exception as e:
            print("error: {}".format(str(e)))
        except:
            print("Error sending pickle")
            
    '''********************************************************************



    NEED TO ADD TIMEOUTS TO RECIEVE FUNCTIONS



    
************************************************************************'''

    def newrecv(self, csock):
        try:
            msg = csock.recv(self.buff_size)
            if not len(msg):
                return (False)
            return (msg)
        except:
            return (False)
        
    def recv_msg_pickle(self):
        while True:
            temp = self.client.recv(self.buff_size)
            try:
                return(pickle.loads(temp))
            except Exception as e:
                print("erro pickle recvr: {}".format(str(e)))
            except:
                print(PiDoor.COMM_ERROR_RECV_MSG_PICKLE)
                return (False)

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
            self.files[i] = FileInfo(os.path.realpath(temp_file_list[i])) 

PAGE="""\
    <html>
    <head>
    <title>Raspberry Pi - Surveillance Camera</title>
    </head>
    <body>
    <center><h1>Raspberry Pi - Surveillance Camera</h1></center>
    <center><img src="stream.mjpg" width="640" height="480"></center>
    </body>
    </html>
    """
IMGHTML1 = """\
<!DOCTYPE html>

<html lang="en" dir="ltr">
    <head>
        <meta charset="utf-8">
        <title></title>
        <link rel="stylesheet" href="style.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/jquery.magnific-popup.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/magnific-popup.min.css" >
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style id="style.css">
            *{
                margin: 0;
                padding: 0;
                font-family: "montserrat",sans-serif;
                box-sizing: border-box;
            }
            .gallery-section{
                width: 100%;
                padding: 60px 0;
                background: #f1f1f1;
            }
            .inner-width{
                width: 100%;
                max-width: 1200px;
                margin: auto;
                padding: 0 20px;
            }
            .gallery-section h1{
                text-align: center;
                text-transform: uppercase;
                color: #333;
            }
            .border{
                width: 180px;
                height: 4px;
                background: #333;
                margin: 60px auto;
            }
            .gallery-section .gallery{
                  display: flex;
                  flex-wrap: wrap-reverse;
                  justify-content: center;

            }
            .gallery-section .image{
                flex: 25%;
                overflow: hidden;
                cursor: pointer;
                padding: 5px
            }
            .gallery-section .image img{
                width: 100%;
                height: 100%;
                transition: 0.4s;
            }
            @media screen and (max-width:960px) {
                .gallery-section .image{
                    flex: 33.33%;
                }
            }
            @media screen and (max-width:768px) {
                .gallery-section .image{
                    flex: 50%;
                }
            }
            @media screen and (max-width:480px) {
                .gallery-section .image{
                    flex: 100%;
                }
            }
        </style>
    </head>
    <body>  
        <div class="gallery-section">
            <div class="inner-width">
                <h1></h1>
                <div class="border"></div> 
                <div class="gallery">
                    """           
IMAGEHTML2 = """\
            </div>
                
            </div>
        </div>
    </body>
                  </html>
                  """

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
    
    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        fileobjects = FileObjs("/home/pi/Documents/473 Project/Project files/", ".jpg")
        fileobjects.setFiles("/home/pi/Documents/473 Project/Project files/")
        print(len(fileobjects.files))
        for i in range(len(fileobjects.files)):
            for j in range(0, len(fileobjects.files)-i-1):
                x = fileobjects.files[j]
                y = fileobjects.files[j+1]
                if(int(x.fileName[2])<int(y.fileName[2])):
                    temp=fileobjects.files[j]
                    fileobjects.files[j] = fileobjects.files[j+1]
                    fileobjects.files[j+1] = temp
        for i in range(len(fileobjects.files)):
            print(fileobjects.files[i].fileName)
                
        PAGE="""\
            <html>
            <head>
            <title>Raspberry Pi - Surveillance Camera</title>
            </head>
            <body>
            <               html += '<img src="' + fileobjects.files[i].fileName + '" alt="test">'
                html += '</a> \n'
                PAGEIMAGES += html
                print(html)

            PAGEIMAGES += IMAGEHTML2
            
            content = PAGEIMAGES.encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        elif self.path == '/'+fileobjects.files[0].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[0].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        elif self.path == '/'+fileobjects.files[1].fileName:
            print(len(fileobjects.files))
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[1].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        elif self.path == '/'+fileobjects.files[2].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[2].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))

        elif self.path == '/'+fileobjects.files[3].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[3].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
                    
        elif self.path == '/'+fileobjects.files[4].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[4].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        elif self.path == '/'+fileobjects.files[5].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[5].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class Stream:center><h1>Raspberry Pi - Surveillance Camera</h1></center>
            <center><img src="stream.mjpg" width="640" height="480"></center>
            <a href = "/images.html"> view images </a>
            </body>
            </html>
            """
        
        PAGE1="""\
            <html>
            <head>
            <title>Raspberry Pi - Surveillance Camera</title>
            </head>
            <body>
            <center><h1>Images</h1></center>
            </body>
            </html>
            """
        
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/images.html':
            PAGEIMAGES = IMGHTML1
            for i in range (len(fileobjects.files)):
                
                html = ""
                html += '<a href="' + fileobjects.files[i].fileName +' " class="image">';
                html += '<img src="' + fileobjects.files[i].fileName + '" alt="test">'
                html += '</a> \n'
                PAGEIMAGES += html
                print(html)

            PAGEIMAGES += IMAGEHTML2
            
            content = PAGEIMAGES.encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        elif self.path == '/'+fileobjects.files[0].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[0].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        elif self.path == '/'+fileobjects.files[1].fileName:
            print(len(fileobjects.files))
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[1].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        elif self.path == '/'+fileobjects.files[2].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[2].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))

        elif self.path == '/'+fileobjects.files[3].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[3].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
                    
        elif self.path == '/'+fileobjects.files[4].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[4].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        elif self.path == '/'+fileobjects.files[5].fileName:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                file = open(fileobjects.files[5].fullPath, "rb")
                t = file.read()
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(t))
                self.end_headers()
                self.wfile.write(t)
                self.wfile.write(b'\r\n')
            
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class Stream:
    def StartStream(self):
        print("starting stream")
        with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
            output = StreamingOutput()
            self.camera = camera
            camera.start_recording(output, format='mjpeg')
            try:
                address = ('', 8000)
                server = StreamingServer(address, StreamingHandler)
                server.serve_forever()
            except Exception as e:
                print("error1: {}".format(str(e)))
            finally:
                camera.stop_recording()

class mystreamer:
    def __init__(self):
        Stream()
