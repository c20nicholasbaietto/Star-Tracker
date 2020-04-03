import os
from time import sleep
import socket
from socket import error as socket_error
import errno

os.chdir("/home/pi/New_Startracker/tests")
os.system("pwd")
#os.system("/bin/bash")
#sleep(1)

#HOST = '127.0.0.1'
#PORT = 8010
file_path = "/home/pi/New_Startracker/tests/picam/samples_GOOD"
#file_path = "/home/pi/oresat-star-tracker-master/openstartracker/tests/picam/samples"
file_type = ".bmp"
ADDR = "./socket"
s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
s.connect(ADDR)
#s.setblocking(0)
#buffer = ''


# Loop awaiting input
while True:
    sleep(0.01)
    image_name = raw_input('Enter command or image name: ')


    try:
        if image_name == "quit":
            s.send(image_name)
            print("\nQutting OpenStartracker\n")
            break
        elif image_name == "lis":
            s.send(image_name)
            reply = s.recv(4096)
            print reply
        else:
            s.sendall(file_path+"/"+image_name+file_type);
            reply = s.recv(4096)
            print reply
            #print("1st")
    except socket_error as serr:
        if serr.errno != errno.EPIPE:
            raise serr
        s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        s.connect(ADDR)
        if image_name == "quit":
            s.send(image_name)
            print("\nQutting OpenStartracker\n")
            break
        s.sendall(file_path+"/"+image_name+file_type);
        reply = s.recv(4096)
        print reply

#os.system("/home/pi/oresat-star-tracker-master/openstartracker/tests/exp2500/samples/3.bmp")
