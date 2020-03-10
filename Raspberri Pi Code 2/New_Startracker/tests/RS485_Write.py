import serial                          # import the module

def banner_top():
    print('   +-------------------------------------------+')
    print('   |   USB2SERIAL RS485 Write in Python 3.x    |')
    print('   |          (c) www.xanthium.in              |')
    print('   +-------------------------------------------+')

def Usage():
    print('   | Windows -> COMxx     eg COM32             |')
    print('   | Linux   ->/dev/ttyS* eg /dev/ttyUSB0      |')
    print('   +-------------------------------------------+')
    
def banner_bottom():
    print('   +-------------------------------------------+')
    print('   |          Press Any Key to Exit            |')
    print('   +-------------------------------------------+')

banner_top()                           # Display the top banner
Usage()
#COM_PortName = input('\n    Enter the COM Port Name ->')
COM_PortName = "/dev/ttyAMA0"

#Opening the serial port

COM_Port = serial.Serial(COM_PortName) # open the COM port
print('\n   ',COM_PortName,'Opened')

COM_Port.baudrate = 9600               # set Baud rate 
COM_Port.bytesize = 8                  # Number of data bits = 8
COM_Port.parity   = 'N'                # No parity
COM_Port.stopbits = 1                  # Number of Stop bits = 1

print('\n    Baud rate = ',COM_Port.baudrate)
print('    Data bits = ',COM_Port.bytesize)
print('    Parity    = ',COM_Port.parity)
print('    Stop bits = ',COM_Port.stopbits)

#Controlling DTR and RTS pins to put USB2SERIAL in transmit mode

COM_Port.setDTR(0) #DTR=0,~DTR=1 so DE = 1,Transmit mode enabled
COM_Port.setRTS(0) #RTS=0,~RTS=1 (In FT232 RTS and DTR pins are inverted)

print('\n    DTR = 0,~DTR = 1 so DE = 1,Transmit mode enabled')
print('    RTS = 0,~RTS = 1')
      
#Write character 'A' to serial port                            
data = bytearray(b'A')                       # Convert Character to byte array 
NoOfBytes  = COM_Port.write(data)            # Write data to serial port

print('\n   ',NoOfBytes,' bytes written')
print('\n    A written to',COM_PortName)
      
COM_Port.close()                       # Close the Serial port

banner_bottom()                        # Display the bottom banner
dummy = input()                        # press any key to close 
