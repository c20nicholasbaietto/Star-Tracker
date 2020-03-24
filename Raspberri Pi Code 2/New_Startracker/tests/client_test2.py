import os
from os import system
from time import sleep, time
import socket
import math
from math import sin, cos
from socket import error as socket_error
import errno
import sys
import cv2
import numpy as np
from fractions import Fraction
import startracker
import beast
import ctypes
import serial
import struct

os.system("pwd")
file_path = sys.argv[1]
CONFIGFILE = sys.argv[2]
YEAR = float(sys.argv[3])
MEDIAN_IMAGE = cv2.imread(sys.argv[4])
command = sys.argv[6]
num_stars = int(sys.argv[7])
is_serial = bool(sys.argv[8])
take_pic = bool(sys.argv[9])
my_star_db = startracker.set_up(CONFIGFILE, YEAR)

if take_pic:
	import picamera
	from cam import set_camera_specs, take_picture

COM_Port = serial.Serial("/dev/ttyS0", baudrate=9600, bytesize =8,parity = 'N', stopbits =1,timeout=300) #open serial port

file_type = ".bmp"
pic_num = 0
start = time()

###### when taking actual pictures, uncomment the code below #######
#camera = picamera.PiCamera()
#set_camera_specs(camera,False)
####################################################################
success_count = 0
total_count = 0
# don't need a star text file anymore
#stars_text_file = sys.argv[5] # text file name with lastest star position data (put a text file and argv in unit_test.sh for it)
stars = None     # latest constellation

# Loop awaiting input
while True:
    before_time = time()
    sleep(0.001) # allows CPU to get ready for next image
    solved = False
    pic_num = pic_num + 1 # cannot read last image
    
    image_name = file_path + "/test" + str(pic_num) + file_type # define image name in while loop instead of outside so we can save all pictures
    
    
    ###### when taking actual pictures, uncomment the code below #######
    image_text = file_path + "/test" + str(pic_num-1) + ".txt" # text file name with useful data (still working on not getting the last image)
    text_file = open(image_text,"w+") # create a text file to write to
    before_capture_time = time()
    if take_pic:
		take_picture(camera, image_name)
    after_capture_time = time()
    ####################################################################
    
    
    if not os.path.exists(image_name):
        print("No picture")
        command = "quit"    

    if command == "quit":
        print("Qutting OpenStartracker")
        break
    elif command == "track" or command == "lis":
        print("pic_num = " + str(pic_num))
        data = image_name.strip() # Remove stray whitespace     
        before_process_time = time() 
        my_reply = startracker.solve_image(file_path, data, pic_num, MEDIAN_IMAGE, my_star_db, stars, num_stars) # solve the image
        after_process_time = time()
        total_count += 1
        if type(my_reply) is tuple: # if the image was solved, this will be true
            new_stars = my_reply[1]
            stars = new_stars
            reply = my_reply[0]
            reply = [x.strip() for x in reply.split(';')]
            solved = True
            print("Quaternian: " + reply[0]) # print the quaternion (this will also need to be returned to the calling function)
            
            q1 = float(reply[4])
            q2 = float(reply[5])
            q3 = float(reply[6])
            q4 = float(reply[7])
            
            my_star_string = ""
            for i in range(len(new_stars)):
                if my_star_string is not "":
                    my_star_string += ","
                my_star_string+="("+str(new_stars[i][0])+","+str(new_stars[i][1])+")"
            
            q = "Quaternian: " + str(reply[0])
            DEC = "DEC: " + str(reply[1])
            RA = "RA: " + str(reply[2])
            ORI = "ORI: " + str(reply[3])
            
            DEC1 = float(reply[1])
            RA1 = float(reply[2])
            ORI1 = float(reply[3])
            
            text_file.write(q+"\n")
            text_file.write(DEC+"\n")
            text_file.write(RA+"\n")
            text_file.write(ORI+"\n")
            text_file.write("Stars: "+my_star_string+"\n")
            
            
            if is_serial:
				print('creating serial command')
				
				
				data = ctypes.create_string_buffer(28)  
				
				#struct.pack_into('ffffffff',data,0,DEC,RA,ORI,QUA1,QUA2,QUA3,QUA4,time)
				struct.pack_into('fffffff',data,0,q1,q2,q3,q4,DEC1,RA1,ORI1)
				print('sending serial command')
				
				COM_Port.write(data)
            
            #print(time())
            success_count += 1
            if command == "lis": # if running lost in space mode, the mode is complete
                ##print("position found :)")
                # return reply[0] <- this is the quaternian that is found from lis mode
                break
        else:
            # if the track fails to solve an image, don't crop next image
            stars = None
            print(my_reply.strip())
        success_per = (float(success_count)/float(total_count)) * 100
        success_per = round(success_per,2)
        print("success rate: " + str(success_per))
        print("fail rate: " + str(100-success_per))
    after_time = time()
    capture_time = after_capture_time - before_capture_time
    process_time = after_process_time - before_process_time
    total_time = after_time - before_time
    text_file.write("Capture Time: "+str(capture_time)+"\n")
    text_file.write("Processing Time: "+str(process_time)+"\n")
    text_file.write("Total Time: " + str(total_time) + "\n")
    print("Capture Time: "+str(capture_time))
    print("Processing Time: "+str(process_time))
    print("Total Time: "+str(total_time)+"\n")
    #stars_text.close()
    text_file.close()

COM_Port.close()

    
