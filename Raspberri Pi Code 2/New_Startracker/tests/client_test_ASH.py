import os
from time import sleep
import socket
import picamera
from socket import error as socket_error
import errno
from fractions import Fraction

os.chdir("/home/pi/New_Startracker/tests")
os.system("pwd")
#os.system("/bin/bash")
#sleep(1)

camera.start_preview()
sleep(200)

#HOST = '127.0.0.1'
#PORT = 8010
#file_path = "/home/pi/oresat-star-tracker-master/openstartracker/tests/exp2500/samples"
file_path = "/home/pi/New_Startracker/tests/demo/Indoor_test_pointing/Indoor_Tests_Capt_K3_2" # folder to put pictures
file_type = ".bmp"
ADDR = "./socket"
#image_name = file_path + "/" + "test1" + file_type
#image_name = "test"+file_type
s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
s.connect(ADDR)
#s.setblocking(0)
#buffer = ''
command = raw_input('Enter command: ')
pic_num = 0

# Loop awaiting input
while True:
    sleep(0.1) #if pictures are not popping up, you may need to increase the sleep time
    pic_num = pic_num + 1
    image_name = file_path + "/test" + str(pic_num) + file_type # define image name in while loop instead of outside so we can save all pictures
    image_text = file_path + "/test" + str(pic_num) + ".txt" # text file with quaternians
    with picamera.PiCamera() as camera:
        #camera.resolution = (1280, 960)
        #camera.iso = 200
        #camera.shutter_speed = 50000
        #
        #camera.framerate = 10
        #camera.zoom = (0.3,0.3,0.5,0.5)
        #camera.color_effects = (128,128)
        #camera.vflip = 1
        #camera.hflip=1
        #camera.rotation = 180
        #camera.capture(image_name)
        #camera.framerate = 1
        
        camera.awb_mode = 'auto'
        camera.exposure_mode = 'night'
        camera.resolution = (1280,960)
        #camera.resolution = (2560,1440)
        camera.iso = 200
        #camera.zoom = (0.35,0.35,0.4,0.4)
        exp_time = 2
        camera.framerate = Fraction(1,exp_time)
        #camera.shutter_speed = exp_time * 1000 * 1000
        camera.shutter_speed = 500000
        print(camera.shutter_speed)
        camera.rotation = 180
        sleep(2)
        #camera.start_preview()
        #sleep(200)
        camera.capture(image_name)

        # Setting the framerate back above 1 allows camera.close() to actually succeed
        camera.framerate = 30
    

    sleep(0.1)
    try:
        if command == "quit":
            s.send(command)
            print("\nQutting OpenStartracker\n")
            break
        elif command == "lis":
            s.sendall(image_name)
            reply = s.recv(4096)
            print reply
            print "pic_num = " + str(pic_num)
        else:
            s.sendall(file_path+"/"+image_name);
            reply = s.recv(4096)
            print reply
            #print("1st")
    except socket_error as serr:
        if serr.errno != errno.EPIPE:
            raise serr
        s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        s.connect(ADDR)
        if command == "quit":
            s.send(image_name)
            print("\nQutting OpenStartracker\n")
            break
        s.sendall(file_path+"/"+image_name);
        reply = s.recv(4096)
        print reply
camera.close()

#os.system("/home/pi/oresat-star-tracker-master/openstartracker/tests/exp2500/samples/3.bmp")
