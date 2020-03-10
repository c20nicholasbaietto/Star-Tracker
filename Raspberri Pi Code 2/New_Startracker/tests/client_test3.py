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

def image_capture(file_path,CONFIGFILE,YEAR,MEDIAN_IMAGE,stars_text_file,command,num_stars):
    ###### when taking actual pictures, uncomment the code below #######
    #import picamera
    #from cam import set_camera_specs, take_picture
    ####################################################################

    #os.chdir("/home/pi/New_Startracker/tests")
    os.system("pwd")
    #os.system("/bin/bash")
    #sleep(1)

    #HOST = '127.0.0.1'
    #PORT = 8010
    #file_path = "/home/pi/oresat-star-tracker-master/openstartracker/tests/exp2500/samples"
    #file_path = "/home/pi/New_Startracker/tests/Indoor_test_pointing/res480480"
    
    #file_path = sys.argv[1]
    #CONFIGFILE = sys.argv[2]
    #YEAR = float(sys.argv[3])
    #MEDIAN_IMAGE = cv2.imread(sys.argv[4])
    #stars_text_file = sys.argv[5] # text file name with lastest star position data (put a text file and argv in unit_test.sh for it)
    #command = sys.argv[6]
    #num_stars = int(sys.argv[7])
    my_star_db = startracker.set_up(CONFIGFILE, YEAR)

    file_type = ".bmp"
    #ADDR = "./socket"
    #image_name = file_path + "/" + "test1" + file_type
    #image_name = "test"+file_type
    #s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    #s.connect(ADDR)
    #s.setblocking(0)
    #buffer = ''
    #command = raw_input('Enter command: ')
    pic_num = 0
    start = time()
    ###### when taking actual pictures, uncomment the code below #######
    #camera = picamera.PiCamera()
    #set_camera_specs(camera,False)
    ####################################################################
    success_count = 0
    total_count = 0
    stars = None     # latest constellation

    # Loop awaiting input
    while True:
        solved = False
        #sleep(0.25) #if pictures are not popping up, you may need to increase the sleep time
        pic_num = pic_num + 1 # cannot read last image
        
        image_name = file_path + "/test" + str(pic_num) + file_type # define image name in while loop instead of outside so we can save all pictures
        #image_name = "test" + str(pic_num) + file_type
        #print(image_name)
        before_time = time()
        
        stars_text = open(stars_text_file,"r") # open the stars.txt file to read from
        prev_stars = stars_text.read()
        prev_stars = prev_stars.strip()
        stars_text.close()
        #print("\""+prev_stars+"\"")
        if prev_stars is not "":
            print("The file is not empty!")
            stars = [x.strip() for x in prev_stars.split(',')] # we have a constellation for the tracking mode
            other_stars = []
            #if len(stars) < 2:
            #    continue
            try:
                for i in range(0,len(stars),2):
                    #print(stars[i])
                    other_stars.append((float(stars[i]),float(stars[i+1])))
                stars = other_stars
            except:
                stars = None
                print("improper read from text file")
        else:
            print("The file is empty!")
            
        stars_text = open(stars_text_file,"w") # open the stars.txt file to write to
        
        ###### when taking actual pictures, uncomment the code below #######
        #image_text = file_path + "/test" + str(pic_num-1) + ".txt" # text file name with useful data (still working on not getting the last image)
        #text_file = open(image_text,"w+") # create a text file to write to
        #take_picture(camera, image_name)
        ####################################################################
        
        
        if not os.path.exists(image_name):
            print("No picture")
            command = "quit"    

        #sleep(0.25)
        if command == "quit":
            #s.send(command)
            print("Qutting OpenStartracker")
            break
        elif command == "track" or command == "lis":
            print("pic_num = " + str(pic_num))
            data = image_name.strip() # Remove stray whitespace             
            my_reply = startracker.solve_image(file_path, data, pic_num, MEDIAN_IMAGE, my_star_db, stars, num_stars) # solve the image
            total_count += 1
            if type(my_reply) is tuple: # if the image was solved, this will be true
                new_stars = my_reply[1]
                reply = my_reply[0]
                reply = [x.strip() for x in reply.split(';')]
                solved = True
                print("Quaternian: " + reply[0]) # print the quaternion (this will also need to be returned to the calling function)
                
                ############################ RS485 Code
                print('creating serial command')
                
                
                q1 = float(reply[4])
                q2 = float(reply[5])
                q3 = float(reply[6])
                q4 = float(reply[7])
                
                
                data = ctypes.create_string_buffer(16)  
                
                #struct.pack_into('ffffffff',data,0,DEC,RA,ORI,QUA1,QUA2,QUA3,QUA4,time)
                struct.pack_into('ffff',data,0,q1,q2,q3,q4)
                print('sending serial command')
                
                COM_Port.write(data)
                
                
                my_star_string = ""
                for i in range(len(new_stars)):
                    if my_star_string is not "":
                        my_star_string += ","
                    my_star_string+=str(new_stars[i][0])+","+str(new_stars[i][1])
                stars_text.write(my_star_string)
                
                #stars_text.write(str(new_stars[0][0])+","+str(new_stars[0][1])+","+str(new_stars[1][0])+","+str(new_stars[1][1])+","+str(new_stars[2][0])+","+str(new_stars[2][1])+","+str(new_stars[3][0])+","+str(new_stars[3][1])+","+str(new_stars[4][0])+","+str(new_stars[4][1]))
                
                ##print("stars: " + str(stars)) # print the stars location      
                #text_file.write(q+"\n")
                #text_file.write(DEC+"\n")
                #text_file.write(RA+"\n")
                #text_file.write(ORI+"\n")
                #print "len reply " + str(len(reply))
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
        process_time = after_time - before_time
        print("Total Time: " + str(process_time) + "\n")

                
        ############################
    #os.system("/home/pi/oresat-star-tracker-master/openstartracker/tests/exp2500/samples/3.bmp")

        
