import os
from os import system
from time import sleep, time
import socket
import sys
import picamera
from socket import error as socket_error
import errno
from fractions import Fraction
from cam import take_picture, set_camera_specs

file_path = "/home/pi/New_Startracker/tests/Indoor_test_pointing/samples"  # open samples folder for calibration
file_type = ".bmp"  # file type of the pictures
#ADDR = "./socket"
#s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
#s.connect(ADDR)
#s.setblocking(0)
#buffer = ''
num_pics = raw_input('Enter number of pictures for calibration: ')
num_pics = int(num_pics)
pic_number = 1
lag_time = 10  # seconds between captures
start = time()

# remove old sample data before calibration
print "\nClearing old sample data:"
system("rm -rfv " + file_path + "/* ")
print "Old data cleared."

camera = picamera.PiCamera()
set_camera_specs(camera, False)

# take the pictures for calibration
for pic_num in range(pic_number, num_pics+1):
    image_name = file_path + "/cal" + str(pic_num) + file_type  # name of calibration pictures
    print "\nTaking picture in..."
    for new_lag_time in range(lag_time, 0, -1):
        print str(new_lag_time)
        sleep(1)
    take_picture(camera, image_name)
    print "Picture taken."

# press enter to calibrate
raw_input('Press any key to commence calibration')

# calibrate the pictures
os.chdir("/home/pi/New_Startracker/tests/")
os.system("./unit_test.sh -c Indoor_test_pointing")

