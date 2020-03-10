from os import listdir, system, environ
from os.path import isfile, join
import cv2
import numpy as np
import sys
from astropy.io import fits
from scipy import spatial
import cPickle as pickle
from shutil import copyfile

#

    # filter the background image for astrometry - more important for starfield generator
    for n in range(0, num_images): # no for loop in cal.py needed

        images[n] -= median_image
        image_name = sys.argv[1] + "/calibration_data/" + basename(image_names[n]) + ".png"
        img = np.clip(images[n], a_min = 0, a_max = 255).astype(np.uint8)
        cv2.imwrite(image_name, img)

        solve_cmd = "solve-field --skip-solved --no-plots" + append + " --cpulimit 60 " + image_name
        print solve_cmd
        system(solve_cmd)

        if isfile(basename(image_name)+'.wcs'):
            # if a picture was solved move it to the calibrated_samples folder
            copyfile(samplepath,calsamplepath) # hopefully will copy all files in samples folder to calibrated_samples folder
            print 'wcsinfo ' + basename(image_name) + '.wcs  | tr [:lower:] [:upper:] | tr " " "=" | grep "=[0-9.-]*$" > ' + basename(image_name) + '.solved'
            system('wcsinfo ' + basename(image_name) + '.wcs  | tr [:lower:] [:upper:] | tr " " "=" | grep "=[0-9.-]*$" > ' + basename(image_name) + '.solved')
            hdulist = fits.open(basename(image_name) + ".corr")
            astrometry_results[image_names[n]] = np.array([[i['flux'], i['field_x'], i['field_y'], i['index_x'], i['index_y']] + angles2xyz(i['index_ra'], i['index_dec']) for i in hdulist[1].data])
    
        system("rm -rfv /home/pi/New_Startracker/tests/Indoor_test_pointing/samples/* ")
    
    
