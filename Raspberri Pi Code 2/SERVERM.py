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
    
    if CommB == b'i':        
        print('Recieved Idle command')
    elif CommB == b'l':
        print('Recieved LIS command')
        os.system("./unit_test.sh -i Indoor_test_pointing")
    elif CommB == b't':
        print('Recieved Tracking command')
        os.system("./unit_test.sh -t Indoor_test_pointing")
    elif CommB == b'c':
        print('Recieved Calibrate command')
        os.system("./unit_test.sh -c Indoor_test_pointing")
    elif CommB == b'r':
        print('Recieved Re-boot command')
        os.system("shutdown /s /t 1")
    else:
        print('Command Not Understood')

