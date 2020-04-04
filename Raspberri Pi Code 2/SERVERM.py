import struct
import ctypes
import serial
import os

os.chdir("New_Startracker/tests/")

COM_Port = serial.Serial("/dev/ttyS0", baudrate=9600, bytesize =8,parity = 'N', stopbits =1,timeout=300) #open serial port

CommRecb = ctypes.create_string_buffer(3) #creates var to recieve command with

con = 'y' # initialise continue var

# n:no last command, i:idle, l:lis, t:tracking, c:calibration
CommN = bytearray(b'n') #create byte array for commands
CommI = bytearray(b'i')
CommL = bytearray(b'l')
CommT = bytearray(b't')
CommC = bytearray(b'c')
CommR = bytearray(b'r')
AddF  = bytearray(b'f') #create byte array for sender address
prevC = bytearray(b'n') #create a byte array for prev. command

while con=='y':
    
    print('looking for command')
    CommRecb = COM_Port.read(3)
    print(CommRecb)
    CommRec= struct.unpack_from('ccc',CommRecb,0)
    AddR = CommRec[0]
    prevC = CommRec[1]
    CommB = CommRec[2]
    num_stars = 5 # number of stars used in tracking mode
    serial = 1 # using serial connection (1 = yes, 0 = no)
    take_pic = 0 # use camera (1 = yes, 0 = no) <- manually change this if you wish to use the camera over the serial connection
    crop = 1 # crop images? (1 = yes, 0 = no) <- manually change if you wish to test effect of not cropping vs. cropping
    # cropping images means you will take the 'num_stars' amount of brightest stars in the image and use those to solve.  
    # This will increase your speed.  The only reason you should change crop to equal 0 is for testing purposes.
    
    if CommB == b'i':        
        print('Recieved Idle command')
        continue
    elif CommB == b'l':
        print('Recieved LIS command')
        cmd = "./unit_test.sh -i Indoor_test_pointing " + str(num_stars) + " " + str(serial) + " " + str(take_pic) + " " + str(crop)
    elif CommB == b't':
        print('Recieved Tracking command')
        cmd = "./unit_test.sh -t Indoor_test_pointing " + str(num_stars) + " " + str(serial) + " " + str(take_pic) + " " + str(crop)
    elif CommB == b'c':
        print('Recieved Calibrate command')
        cmd = "./unit_test.sh -c Indoor_test_pointing " + str(num_stars) + " " + str(serial) + " " + str(take_pic) + " " + str(crop)
    elif CommB == b'r':
        print('Recieved Re-boot command')
        cmd = "shutdown /s /t 1"
    else:
        print('Command Not Understood')
        continue
    
    print(cmd)
    
    os.system(cmd)

