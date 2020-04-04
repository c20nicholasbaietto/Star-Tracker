# modified by Nicholas Baietto, from the USAF Academy - Department of Astronuatics
# cam_old.py - allows the user to either take a picture or preview with the picamera.
# Per cam.py - previews will last 1000 seconds and can be ended by hitting CTRL C in the terminal

from picamera import PiCamera
from time import sleep, time
from fractions import Fraction
from cam import take_picture, set_camera_specs

# Exposure time in seconds or "auto" for
# automatic exposure time
exp_time = 2  # "auto" #change 'auto' to a number to set the exposure time to that number (in seconds)
preview = raw_input('Preview? (y/n): ')

file_path = "/home/pi/New_Startracker/tests/Indoor_test_pointing/samples/"
file_type = ".bmp"
#ADDR = "./socket"

start = time()
my_camera = PiCamera()
PiCamera.CAPTURE_TIMEOUT = 120  # seconds

set_camera_specs(my_camera, preview)
if preview is not 'y':
	name = raw_input('Enter Image Name: ')
	image_name = file_path + "/" + name + file_type
	take_picture(my_camera, image_name)

print("total time:\t" + str(time() - start))
test_shutter_speed = my_camera.exposure_speed
print(test_shutter_speed)
print("Close")
my_camera.close()
print("Done")
