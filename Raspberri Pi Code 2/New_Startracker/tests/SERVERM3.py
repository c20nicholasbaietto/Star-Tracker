import struct
import ctypes
import serial
import os
from client_test3 import image_capture

TESTDIR = "Indoor_test_pointing"

#COM_Port = serial.Serial("/dev/tty1", baudrate=9600, bytesize =8,parity = 'N', stopbits =1,timeout=300) #open serial port
COM_Port = serial.Serial("/dev/ttyS0", baudrate=9600, bytesize =8,parity = 'N', stopbits =1,timeout=300) #open serial port

CommRecb = ctypes.create_string_buffer(3) #creates var to recieve command with

con = 'y' # initialise continue var

# n:no last command, i:idle, l:lis, t:tracking, c:calibration
CommN = bytearray(b'n') #create byte array for commands
CommI = bytearray(b'i')
CommL = bytearray(b'l')
CommT = bytearray(b't')
CommC = bytearray(b'c')
CommO = bytearray(b'o')
AddF = bytearray(b'f') #create byte array for sender address
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
        print('Recieved idle command')
    elif CommB == b'l':
        print('Recieved LIS command')
        #$TESTDIR/res480480 $TESTDIR/calibration.txt 1991.25 $TESTDIR/median_image.png $TESTDIR/stars.txt track 5
        print(TESTDIR+"/res480480")
        image_capture(TESTDIR+"/res480480",TESTDIR+"/calibration.txt",1991.25,TESTDIR+"/median_image.png",TESTDIR+"/stars.txt","track",5)
    elif CommB == b't':
        print('Recieved tracking command')
        os.system("./unit_test.sh -t Indoor_test_pointing")
    elif CommB == b'c':
        print('Recieved calibrate command')
        os.system("./unit_test.sh -c Indoor_test_pointing")
    elif CommB == b'o':
        print('Recieved off command')
        con=='n'
    else:
    
        DEC =  76868578
        RA =   63645746
        ORI =  99999999
        QUA1 = 67647557
        QUA2 = 94646746
        QUA3 = 97874575
        QUA4 = 57645746
        time = 12323435
    
        struct.pack_into('ffffffff',data,0,DEC,RA,ORI,QUA1,QUA2,QUA3,QUA4,time)
    
        COM_Port.write(data)
    
        print(data)
    
COM_Port.write(signoff)
COM_Port.close()                # Close the Serial port
    

