import struct
import ctypes
import serial
import sys
import os

file_path = os.getcwd()

COM_Port = serial.Serial("/dev/ttyUSB0", baudrate=9600, bytesize =8,parity = 'N', stopbits =1,timeout=300) #open serial port

print('    Baud rate = ',COM_Port.baudrate)
print('    Data bits = ',COM_Port.bytesize)
print('    Parity    = ',COM_Port.parity)
print('    Stop bits = ',COM_Port.stopbits)



def comm_banner():
    print('   +-------------------------------------------+')
    print('   |   RS485 Connection has been established   |')
    print('   |   The follow commands are available:      |')
    print('   |   Press 1: Idle Command                   |')
    print('   |   Press 2: Calibrate Command              |')
    print('   |   Press 3: Lost In Space Command          |')
    print('   |   Press 4: Tracking Command               |')
    print('   |   Press 5: Off Command                    |')
    print('   +-------------------------------------------+')
    
def signoff():
    print('   +-------------------------------------------+')
    print('   |   FlComm has been closed                  |')
    print('   +-------------------------------------------+')

Comm = ctypes.create_string_buffer(3) #creates var to send command with
data = ctypes.create_string_buffer(32) #creates var for read back data

con   = 'y' # initialise continue var
cont = 'y' 
# n:no last command, i:idle, l:lis, t:tracking, c:calibration r: reboot
CommN = b'n' #create byte array for commands
CommI = b'i'
CommL = b'l'
CommT = b't'
CommC = b'c'
CommR = b'r '
AddrF = b'f' #create byte array for sender address
CurrC = b'n' #create a byte array for prev. command

comm_banner()
counter = 0
num_files = 5
while con=='y':
    counter = counter%5
    counter = counter + 1
    image_text = file_path + "/test" + str(counter) + ".txt" # text file name with useful data
    text_file = open(image_text,"w+") # create a text file to write to
    
    inputcomm = raw_input("Enter your desired command: ")
    
    if inputcomm == "1":   # Idle command
        struct.pack_into('ccc',Comm,0,AddrF,CurrC,CommI)
        COM_Port.write(Comm)
        CurrC = b'i'
        print('Idle Command sent')
            
    elif inputcomm == "2": # Calibrate command
        struct.pack_into('ccc',Comm,0,AddrF,CurrC,CommC)
        COM_Port.write(Comm)
        CurrC = b'c'
        print('Calibrate Command sent')
            
    elif inputcomm == "3": # LIS command
        struct.pack_into('ccc',Comm,0,AddrF,CurrC,CommL)
        COM_Port.write(Comm)
        print('LIS Command sent')
        data = COM_Port.read(28)
        dataRet = struct.unpack_from('fffffff',data,0)
        print(dataRet)
        text_file.write('Orientation Received {0}'.format(dataRet))
        CurrC = b'l'
            
    elif inputcomm == "4": # tracking mode command
        struct.pack_into('ccc',Comm,0,AddrF,CurrC,CommT)
        COM_Port.write(Comm)
        CurrC = b't'
        print('Tracking Command sent')
        
        while cont == 'y':
            data = COM_Port.read(28)
            dataRet = struct.unpack_from('fffffff',data,0)
            print(dataRet)
            text_file.write('Orientation Received {0}'.format(dataRet))
            #cont = raw_input("Would you like to continue tracking? y or n: ")
        struct.pack_into('ccc',Comm,0,AddrF,CurrC,CommI)
        COM_Port.write(Comm)
        
    elif inputcomm == "5": # Off command
        struct.pack_into('ccc',Comm,0,AddrF,CurrC,CommR) # doesn't work
        COM_Port.write(Comm)
        CurrC = b'n'
        print('Off Command sent')
        
    else:
        print("Command was not understood")
    
    text_file.close()
    con = raw_input("Would you like to send another command? y or n: ")
    cont = 'y'

#COM_Port.write(signoff) 
COM_Port.close() # Close the Serial port

