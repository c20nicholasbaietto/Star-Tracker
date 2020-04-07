# modified by Nicholas Baietto, from the USAF Academy - Department of Astronuatics
# server.py - builds command to run on startracker pi

# You can also run the built command in the terminal in the "New_Startracker/tests/" 
# directory if you so desire. A built command would look like "./unit_test.sh -t Indoor_test_pointing 5 0 0 1".
# 5 = num_stars, 0 = not using the serial connection, 0 = not taking a picture, 1 = cropping image (in that order).
# When running the command in the terminal, take out the quotes.

import os

os.chdir("New_Startracker/tests/")

my_cmd = raw_input("Enter command: ('r' - recompile, 'c' - calibrate, 't' - tracking mode, 'i' - lis mode): ")
num_stars = 5 # number of stars tracking mode "crops" (change for testing if need be.  Otherwise keep at 5)
serial = 0 # if running from star_tracker pi, leave as 0. (which you are so don't change this value)
crop = 0 # see below for functionality of crop.  Do not change this value
if my_cmd is not 'r':
	take_pic = raw_input("Do you want to take pictures 'y' or 'n': ")
	if take_pic == 'y':
		take_pic = 1
	else:
		take_pic = 0
	if my_cmd == 't':
		crop = raw_input("Do you want to crop images 'y' or 'n': ")
		# cropping images means you will take the 'num_stars' amount of brightest stars in the image and use those to solve.  
		# This will increase your speed.  The only reason you should say no to this prompt is for testing purposes.
		if crop == 'y':
			crop = 1
		else:
			crop = 0
	# create command to be executed by os
	cmd = "./unit_test.sh -" + my_cmd + " Indoor_test_pointing " + str(num_stars) + " " + str(serial) + " " + str(take_pic) + " " + str(crop)
else:
	# create command to be executed by os
	cmd = "./unit_test.sh -" + my_cmd + " Indoor_test_pointing "

os.system(cmd)
# -r = recompile C code if chage the C code
# -i = lost in space (lis) mode
# -c = autonomous calibration mode
# -t = tracking mode
