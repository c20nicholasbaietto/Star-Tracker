# startracker.py - main front-end for the star tracker
# by Umair Khan, from the Portland State Aerospace Society
# based on OpenStarTracker from Andrew Tennenbaum at the University of Buffalo


# Imports
from time import time
from time import sleep
import math
from math import sin
from math import cos
import sys
import os
import cv2
import socket
import numpy as np
import beast

myStartTime = time()
# Prepare constants and get system arguments
P_MATCH_THRESH = 0.99
CONFIGFILE = sys.argv[1]
YEAR = float(sys.argv[2])
MEDIAN_IMAGE = cv2.imread(sys.argv[3])
SOCKET_ADDR = "./socket"
#SOCKET_ADDR = "(127.0.0.1,8010)"
try:
    os.unlink(SOCKET_ADDR)
except OSError:
    if os.path.exists(SOCKET_ADDR):
        raise
BUFFER_SIZE = 4096
data = ""
b_conf = [time(), beast.cvar.PIXSCALE, beast.cvar.BASE_FLUX]

# Prepare socket
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)    
print "Socket created"
  
# Bind to the port 
s.bind(SOCKET_ADDR)         
print "Socket bound to %s" %(SOCKET_ADDR)

# Prepare star tracker
print "\nLoading config" 
beast.load_config(CONFIGFILE)

print "Loading hip_main.dat" 
S_DB = beast.star_db()
S_DB.load_catalog("hip_main.dat", YEAR)

print "Filtering stars" 
SQ_RESULTS = beast.star_query(S_DB)
SQ_RESULTS.kdmask_filter_catalog()
SQ_RESULTS.kdmask_uniform_density(beast.cvar.REQUIRED_STARS)
S_FILTERED = SQ_RESULTS.from_kdmask()

print "Generating DB" 
C_DB = beast.constellation_db(S_FILTERED, 2 + beast.cvar.DB_REDUNDANCY, 0)

print "Ready"


# Utility function to see if an image is worth solving
def check_image(img, connection):

    # Generate test parameters
    height, width, channels = img.shape
    total_pixels = height * width
    blur_check = int(total_pixels * 0.99996744)
    too_many_check = int(total_pixels * 0.99918619)

    # Convert and threshold the image
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ret, threshold = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY)

    # Count the number of black pixels in the thresholded image
    threshold_black = total_pixels - cv2.countNonZero(threshold)

    # Check the test values and return appropriate value
    if threshold_black > blur_check:

        blur = cv2.Laplacian(img, cv2.CV_64F).var()

        if blur != 0 and blur < 5:
            connection.send("Image too blurry")
        else:
            connection.send("Too few stars in image")

        return 0

    elif threshold_black < too_many_check:
        connection.send("Image has too many stars or is not a pure star field")
        return 0

    return 1


# Solution function
def solve_image(filepath, connection):

    # Keep track of solution time
    starttime = time()

    # Create and initialize variables
    img_stars = beast.star_db()
    match = None
    fov_db = None

    # Start output for iteration
    #connection.send("\n\n" + filepath)
    
    # Load and check if the image is worth processing
    img = cv2.imread(filepath)
    result = check_image(img, connection)

    # If the image failed testing, skip it
    if result == 0:
        connection.send("\nTime: " + str(time() - starttime))
        return

    # Process the image for solving
    img = np.clip(img.astype(np.int16) - MEDIAN_IMAGE, a_min = 0, a_max = 255).astype(np.uint8)
    img_grey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Remove areas of the image that don't meet our brightness threshold and then extract contours
    ret, thresh = cv2.threshold(img_grey, beast.cvar.THRESH_FACTOR * beast.cvar.IMAGE_VARIANCE, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, 1, 2); # thresh_contours was the first output, but nah

    # Process the contours
    for c in contours:

        M = cv2.moments(c)

        if M['m00'] > 0:

            # this is how the x and y position are defined by cv2
            cx = M['m10'] / M['m00']
            cy = M['m01'] / M['m00']

            # see https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/ for how to convert these into eigenvectors/values
            u20 = M["m20"] / M["m00"] - cx ** 2
            u02 = M["m02"] / M["m00"] - cy ** 2
            u11 = M["m11"] / M["m00"] - cx * cy

            # The center pixel is used as the approximation of the brightest pixel
            img_stars += beast.star(cx - beast.cvar.IMG_X / 2.0, (cy - beast.cvar.IMG_Y / 2.0), float(cv2.getRectSubPix(img_grey, (1,1), (cx,cy))[0,0]), -1)

        # For the first pass, we only want to use the brightest MAX_FALSE_STARS + REQUIRED_STARS
        img_stars_n_brightest = img_stars.copy_n_brightest(beast.cvar.MAX_FALSE_STARS + beast.cvar.REQUIRED_STARS)
        img_const_n_brightest = beast.constellation_db(img_stars_n_brightest, beast.cvar.MAX_FALSE_STARS + 2, 1)
        lis = beast.db_match(C_DB, img_const_n_brightest)
        
    myElapsedTime1 = time() - starttime
    print("Process Time Before Search = " + str(myElapsedTime1))
    # Generate the match
    if lis.p_match > P_MATCH_THRESH and lis.winner.size() >= beast.cvar.REQUIRED_STARS:

        x = lis.winner.R11
        y = lis.winner.R21
        z = lis.winner.R31
        r = beast.cvar.MAXFOV / 2

        SQ_RESULTS.kdsearch(x, y, z, r, beast.cvar.THRESH_FACTOR * beast.cvar.IMAGE_VARIANCE)
        
        # estimate density for constellation generation
        C_DB.results.kdsearch(x, y, z, r,beast.cvar.THRESH_FACTOR * beast.cvar.IMAGE_VARIANCE)
        fov_stars = SQ_RESULTS.from_kdresults()
        fov_db = beast.constellation_db(fov_stars, C_DB.results.r_size(), 1)
        C_DB.results.clear_kdresults()
        SQ_RESULTS.clear_kdresults()
        
        img_const = beast.constellation_db(img_stars, beast.cvar.MAX_FALSE_STARS + 2, 1)
        near = beast.db_match(fov_db, img_const)

        if near.p_match > P_MATCH_THRESH:
            match = near
        myElapsedTime2 = time() - myElapsedTime1 - starttime
        print("Search Time = " + str(myElapsedTime2))
    # Print solution
    if match is not None:
        a = match.winner.print_ori()
        print("\n")
        DEC = a[0]*(math.pi/180)
        RA = a[1]*(math.pi/180)
        ORI = a[2]*(math.pi/180)
    
        #rot_1st = np.array([[cos(ORI),sin(ORI),0],[-sin(ORI),cos(ORI),0],[0,0,1]])
        #rot_2nd = np.array([[1,0,0],[0,cos(DEC),sin(DEC)],[0,-sin(DEC),cos(DEC)]])
        #rot_3rd = np.array([[cos(RA),sin(RA),0],[-sin(RA),cos(RA),0],[0,0,1]])

        rot_1st = np.array([[1,0,0],[0,cos(ORI),sin(ORI)],[0,-sin(ORI),cos(ORI)]])
        #print(rot_1st)
        rot_2nd = np.array([[cos(-DEC),0,-sin(-DEC)],[0,1,0],[sin(-DEC),0,cos(-DEC)]])
        #print(rot_2nd)
        rot_3rd = np.array([[cos(RA),sin(RA),0],[-sin(RA),cos(RA),0],[0,0,1]])
        #print(rot_3rd)
        DCM = np.transpose(np.matmul(np.matmul(rot_1st,rot_2nd),rot_3rd))

        #print(DCM)
        
        q4=0.5*np.sqrt(1+np.trace(DCM));
        q1=1/(4*q4)*(DCM[1,2]-DCM[2,1]);
        q2=1/(4*q4)*(DCM[2,0]-DCM[0,2]);
        q3=1/(4*q4)*(DCM[0,1]-DCM[1,0]);
        q = (str(q4)+" "+str(q1)+"i "+str(q2)+"j "+str(q3)+"k\n")
        


        #attitude1 = ("\nDEC = "+str(a[0]));
        #attitude2 = ("RA = "+str(a[1]));
        #attitude3 = ("ORIENTATION = "+str(a[2]));
        #attitude = (attitude1+"\n"+attitude2+"\n"+attitude3+"\n");

        #connection.sendall("\n"+attitude+"\nTime: " + str(time() - starttime)+"\n")
        connection.sendall("\nQuaternion:\n"+q+"\nTime: " + str(time() - starttime)+"\n")
        #connection.sendall("\nDEC = "+DEC+"\nRA = "+RA+"\nORI = "+ORI+"\nQuaternion:\n"+q+"\nTime: " + str(time() - starttime)+"\n")
        #connection.sendall("\nTime: " + str(time() - starttime)+"\n")
        #return attitude

        # For reference:
        # - DEC         - rotation about the y-axis
        # - RA          - rotation about the z-axis
        # - ORIENTATION - rotation about the camera axis

    else:
        connection.sendall("\nImage could not be processed; no match found\n")
        print("Image could not be solved\n")

    # Calculate how long it took to process
    #connection.send("\nTime: " + str(time() - starttime)+"\n")


# Put socket in istening mode 
s.listen(5)      
print "\nSocket is listening"   

# Listen for connections until broken

c, addr = s.accept()
c.send("Received connection\n")   

while True: 
    
    # Establish connection with client. 
    #c, addr = s.accept()
    #c.send("Received connection\n")  

    # Receive data w/ CYA policy
    try:
        data = c.recv(BUFFER_SIZE)
    except:
        c.sendall("An error occurred, closing link\n")

    # Remove stray whitespace
    data = data.strip()

    # Execute appropriate action
    if data == "quit":
        #c.send("Shutting down OpenStarTracker, closing link...\n")
        print("Shutting down OpenStarTracker, closing link...\n")
        c.close()
        break
    elif data == "lis":
        print("\nStarting.  Now awaiting commands.\n")
        #c.sendall("\nStarting.  Now awaiting commands.\n")
    else:
        solve_image(data,c)
        #attitude = solve_image(data, c)
        #if attitude != None:
            #c.senda("\n"+attitude)
        #else:
        #   print("Image did not solve\n")
        #   c.send("\nImage did not solve\n")
        
    
    #c.close()

#print "\n"
