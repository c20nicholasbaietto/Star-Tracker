from picamera import PiCamera
from time import sleep, time
from fractions import Fraction

def set_camera_specs(camera, prev):
    camera.awb_mode = 'auto'
    camera.exposure_mode = 'night'
    # camera.resolution = (1280,960)
    camera.resolution = (480, 480)
    # camera.resolution = (2560,1440)
    camera.iso = 800
    # camera.zoom = (0.35,0.35,0.4,0.4)
    #exp_time = 2
    #camera.framerate = Fraction(1,exp_time)
    # camera.shutter_speed = exp_time * 1000 * 1000
    camera.shutter_speed = 6000000
    print(camera.shutter_speed)
    camera.rotation = 180
    if prev == 'y':
        camera.start_preview()
        sleep(1000)


def take_picture(camera, img_name):
    before = time()
    camera.capture(img_name)
    print("\ncapture time:\t" + str(time() - before) + "\n")
    
