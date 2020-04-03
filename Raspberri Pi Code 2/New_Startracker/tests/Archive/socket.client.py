import socket

#HOST = '127.0.0.1'
#PORT = 8010
ADDR = "./Nate_Aday"
s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
s.connect(ADDR)

# Loop awaiting input
while True:
	command = raw_input('Enter your command: ')
	s.send(command)
	reply = s.recv(1024)
	if reply == 'Terminate':
		break
	print reply