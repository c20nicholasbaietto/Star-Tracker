import time
import serial

#ser = serial.Serial(
#    port = '/dev/ttyAMA0',
#    baudrate = 115200,
#    parity = serial.PARITY_NONE,
#    stopbits = serial.STOPBITS_ONE
#    bytesize = serial.EIGHTBITS,
#    timeout =1)#
#
#while True:
#    ser.write(b'x\n')
#    time.sleep(2)

ser = serial.Serial('/dev/ttyAMA0')
print(ser.name)
while True:
    x = raw_input("Send via serial:  ")
    ser.write(b'hello')
    if x == "quit":
        break