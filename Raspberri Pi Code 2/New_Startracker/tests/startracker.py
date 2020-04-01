# startracker.py - main front-end for the star tracker
# by Nick Baietto, from the USAF Academy - Department of Astronuatics
# based on code from Umair Khan, from the Portland State Aerospace Society
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

# Prepare constants and get system arguments
P_MATCH_THRESH = 0.99


# figure out how to initialize the above variables.  Otherwise just pass them in to the below functions in client_test2.py

# SOCKET_ADDR = "./socket"
# SOCKET_ADDR = "(127.0.0.1,8010)"
# try:
#    os.unlink(SOCKET_ADDR)
# except OSError:
#    if os.path.exists(SOCKET_ADDR):
#        raise
# BUFFER_SIZE = 4096
# data = ""
# b_conf = [time(), beast.cvar.PIXSCALE, beast.cvar.BASE_FLUX]

# Prepare socket
# s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# print("Socket created")

# Bind to the port 
# s.bind(SOCKET_ADDR)
# print("Socket bound to " + SOCKET_ADDR)

class star_database:
    def __init__(self, CONFIGFILE, YEAR, S_DB, SQ_RESULTS, S_FILTERED, C_DB):
        self.CONFIGFILE = CONFIGFILE
        self.YEAR = YEAR
        self.S_DB = S_DB
        self.SQ_RESULTS = SQ_RESULTS
        self.S_FILTERED = S_FILTERED
        self.C_DB = C_DB


def set_up(CONFIGFILE, YEAR):
    # Prepare star tracker
    print("\nLoading config")
    print(CONFIGFILE)
    beast.load_config(CONFIGFILE)

    print("Loading hip_main.dat")
    S_DB = beast.star_db()
    S_DB.load_catalog("hip_main.dat", YEAR)

    print("Filtering stars")
    SQ_RESULTS = beast.star_query(S_DB)
    SQ_RESULTS.kdmask_filter_catalog()
    SQ_RESULTS.kdmask_uniform_density(beast.cvar.REQUIRED_STARS)
    S_FILTERED = SQ_RESULTS.from_kdmask()
    # print(SQ_RESULTS)
    # print(S_FILTERED)

    print("Generating DB")
    C_DB = beast.constellation_db(S_FILTERED, 2 + beast.cvar.DB_REDUNDANCY, 0)
    # print(C_DB)

    print("Ready\n")
    return star_database(CONFIGFILE, YEAR, S_DB, SQ_RESULTS, S_FILTERED, C_DB)


# Utility function to see if an image is worth solving
def check_image(img):
    # Generate test parameters
    height, width, channels = img.shape
    total_pixels = height * width
    ##print("height2: " + str(height))
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
            return "Image too blurry"
        else:
            return "Too few stars in image"

    elif threshold_black < too_many_check:
        return "Image has too many stars or is not a pure star field"

    return ""


# Solution function
def solve_image(directory, filepath, pic_num, MEDIAN_IMAGE, my_star_db, star_position, num_stars, my_track):
    # Keep track of solution time
    # print(time())
    start_time = time()

    CONFIGFILE = my_star_db.CONFIGFILE
    YEAR = my_star_db.YEAR
    S_DB = my_star_db.S_DB
    SQ_RESULTS = my_star_db.SQ_RESULTS
    S_FILTERED = my_star_db.S_FILTERED
    C_DB = my_star_db.C_DB

    # Create and initialize variables
    img_stars = beast.star_db()
    match = None
    fov_db = None

    # Start output for iteration
    # connection.send("\n\n" + filepath)

    # Load and check if the image is worth processing
    img = cv2.imread(filepath)

    height, width, channels = img.shape  # height and width used for cropping
    ##print("height: "+str(height))

    # if a previous star positions are known, only use those stars
    if star_position is not None:
        star_positions = list(star_position)
        x_offset = height / 2
        y_offset = width / 2
        # shift the center to the top left corner for image processing
        for i in range(0, len(star_positions)):
            star_positions[i] = list(star_positions[i])
            star_positions[i][0] += x_offset
            star_positions[i][1] += y_offset
            star_positions[i] = tuple(star_positions[i])

        ##### Uncomment code below for multiple blacked out stars ######
        cv2.imwrite(directory + "/black" + str(pic_num) + "i.bmp", img)
        before = time()
        whiteFrame = 255 * np.ones((width, height, 3), np.uint8)
        tolerance = 20
        for i in range(0, len(star_positions)):
            min_y = int(star_positions[i][1] - tolerance)
            max_y = int(star_positions[i][1] + tolerance)
            min_x = int(star_positions[i][0] - tolerance)
            max_x = int(star_positions[i][0] + tolerance)
            if max_x > height: max_x = height
            if min_x < 0: min_x = 0
            if max_y > width: max_y = width
            if min_y < 0: min_y = 0
            c_height = max_x - min_x
            c_width = max_y - min_y
            blackFrame = 0 * np.ones((c_width, c_height, 3), np.uint8)
            whiteFrame[min_y:max_y, min_x:max_x] = blackFrame
        cv2.imwrite(directory + "/black" + str(pic_num) + "o.bmp", whiteFrame)
        if my_track:
            img = np.clip(img.astype(np.int16) - whiteFrame, a_min=0, a_max=255).astype(np.uint8)
        cv2.imwrite(directory + "/black" + str(pic_num) + "f.bmp", img)
    ################################################################

    result = check_image(img)
    # print(time())

    # If the image failed testing, skip it
    if len(result) > 0:
        send_time = "\nTime: " + str(time() - start_time) + "\n" + result
        # connection.send("\nTime: " + str(time() - start_time))
        return send_time

    # Process the image for solving
    img = np.clip(img.astype(np.int16) - MEDIAN_IMAGE, a_min=0, a_max=255).astype(np.uint8)
    img_grey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Remove areas of the image that don't meet our brightness threshold and then extract contours
    ret, thresh = cv2.threshold(img_grey, beast.cvar.THRESH_FACTOR * beast.cvar.IMAGE_VARIANCE, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, 1, 2);  # thresh_contours was the first output, but nah
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
            img_stars += beast.star(cx - width / 2.0, (cy - height / 2.0),
                                    float(cv2.getRectSubPix(img_grey, (1, 1), (cx, cy))[0, 0]), -1)

        # For the first pass, we only want to use the brightest MAX_FALSE_STARS + REQUIRED_STARS
        img_stars_n_brightest = img_stars.copy_n_brightest(beast.cvar.MAX_FALSE_STARS + beast.cvar.REQUIRED_STARS)
        img_const_n_brightest = beast.constellation_db(img_stars_n_brightest, beast.cvar.MAX_FALSE_STARS + 2, 1)
        # print(C_DB)
        lis = beast.db_match(C_DB, img_const_n_brightest)
        # print(lis)
    stars = []
    t_const = []
    # print(num_stars)
    if num_stars > img_stars_n_brightest.size():
        num_stars = img_stars_n_brightest.size()
    # print("size: " + str((img_stars_n_brightest.size())))
    for i in range(img_stars_n_brightest.size()):
        # print("star" + str(i) + ": (" + str(img_stars_n_brightest.get_star(i).px) + ", " + str(img_stars_n_brightest.get_star(i).py) + ")")
        if i < num_stars:
            stars.append((img_stars_n_brightest.get_star(i).px, img_stars_n_brightest.get_star(i).py))

    myElapsedTime1 = time() - start_time
    # print("Process Time Before Search = " + str(myElapsedTime1))
    # Generate the match
    if lis.p_match > P_MATCH_THRESH and lis.winner.size() >= beast.cvar.REQUIRED_STARS:

        x = lis.winner.R11
        y = lis.winner.R21
        z = lis.winner.R31
        r = beast.cvar.MAXFOV / 2

        SQ_RESULTS.kdsearch(x, y, z, r, beast.cvar.THRESH_FACTOR * beast.cvar.IMAGE_VARIANCE)

        # estimate density for constellation generation
        C_DB.results.kdsearch(x, y, z, r, beast.cvar.THRESH_FACTOR * beast.cvar.IMAGE_VARIANCE)
        fov_stars = SQ_RESULTS.from_kdresults()
        fov_db = beast.constellation_db(fov_stars, C_DB.results.r_size(), 1)
        C_DB.results.clear_kdresults()
        SQ_RESULTS.clear_kdresults()

        img_const = beast.constellation_db(img_stars, beast.cvar.MAX_FALSE_STARS + 2, 1)
        near = beast.db_match(fov_db, img_const)
        # print(near.p_match)
        if near.p_match > P_MATCH_THRESH:
            match = near
        myElapsedTime2 = time() - myElapsedTime1 - start_time
        # print("Search Time = " + str(myElapsedTime2))
    # Print solution
    if match is not None:
        a = match.winner.print_ori()
        # print("\n")
        DEC = a[0] * (math.pi / 180)
        RA = a[1] * (math.pi / 180)
        ORI = a[2] * (math.pi / 180)

        # rot_1st = np.array([[cos(ORI),sin(ORI),0],[-sin(ORI),cos(ORI),0],[0,0,1]])
        # rot_2nd = np.array([[1,0,0],[0,cos(DEC),sin(DEC)],[0,-sin(DEC),cos(DEC)]])
        # rot_3rd = np.array([[cos(RA),sin(RA),0],[-sin(RA),cos(RA),0],[0,0,1]])

        rot_1st = np.array([[1, 0, 0], [0, cos(ORI), sin(ORI)], [0, -sin(ORI), cos(ORI)]])
        # print(rot_1st)
        rot_2nd = np.array([[cos(-DEC), 0, -sin(-DEC)], [0, 1, 0], [sin(-DEC), 0, cos(-DEC)]])
        # print(rot_2nd)
        rot_3rd = np.array([[cos(RA), sin(RA), 0], [-sin(RA), cos(RA), 0], [0, 0, 1]])
        # print(rot_3rd)
        DCM = np.transpose(np.matmul(np.matmul(rot_1st, rot_2nd), rot_3rd))

        # print(DCM)

        q4 = 0.5 * np.sqrt(1 + np.trace(DCM))
        q1 = 1 / (4 * q4) * (DCM[1, 2] - DCM[2, 1])
        q2 = 1 / (4 * q4) * (DCM[2, 0] - DCM[0, 2])
        q3 = 1 / (4 * q4) * (DCM[0, 1] - DCM[1, 0])
        q = str(q4) + " " + str(q1) + "i " + str(q2) + "j " + str(q3) + "k"
        # q = str(q4)+" "+str(q1)+"i "+str(q2)+"j "+str(q3) <- old one didn't have k term.

        # attitude1 = ("\nDEC = "+str(a[0]));
        # attitude2 = ("RA = "+str(a[1]));
        # attitude3 = ("ORIENTATION = "+str(a[2]));
        # attitude = (attitude1+"\n"+attitude2+"\n"+attitude3+"\n");

        # connection.sendall("\n"+attitude+"\nTime: " + str(time() - start_time)+"\n")
        my_time = time() - start_time
        erythin = q + ";" + str(DEC * (180 / math.pi)) + ";" + str(RA * (180 / math.pi)) + ";" + str(
            ORI * (180 / math.pi)) + ";" + \
                  str(q1) + ";" + str(q2) + ";" + str(q3) + ";" + str(q4)
        # print(erythin)
        # print(time())
        return (erythin, stars)
        # connection.sendall("\nQuaternion:\n"+q+"\nTime: " + str(time() - start_time)+"\n")
        # connection.sendall("\nDEC = "+DEC+"\nRA = "+RA+"\nORI = "+ORI+"\nQuaternion:\n"+q+"\nTime: " + str(time() - start_time)+"\n")
        # connection.sendall("\nTime: " + str(time() - start_time)+"\n")
        # return attitude

        # For reference:
        # - DEC         - rotation about the y-axis
        # - RA          - rotation about the z-axis
        # - ORIENTATION - rotation about the camera axis

    else:
        # print(time())
        return "\nImage could not be processed, no match found\n"
    # print("Image could not be solved\n")

    # Calculate how long it took to process
    # connection.send("\nTime: " + str(time() - start_time)+"\n")

# def useless_code()
# Put socket in istening mode
#	s.listen(5)      
#	print("\nSocket is listening")

# Listen for connections until broken

#	c, addr = s.accept()
#	c.send("Received connection\n")   

#	while True: 

# Establish connection with client.
# c, addr = s.accept()
# c.send("Received connection\n")

# Receive data w/ CYA policy
#		try:
#			data = c.recv(BUFFER_SIZE)
#		except:
#			c.sendall("An error occurred, closing link\n")

# Remove stray whitespace
#		data = data.strip()
#		print(data)

# Execute appropriate action
#		if data == "quit":
# c.send("Shutting down OpenStarTracker, closing link...\n")
#			print("Shutting down OpenStarTracker, closing link...\n")
#			c.close()
#			break
#		elif data == "lis":
#			print("\nStarting.  Now awaiting commands.\n")
# c.sendall("\nStarting.  Now awaiting commands.\n")
#		else:
#			solve_image(data,c)
# attitude = solve_image(data, c)
# if attitude != None:
# c.senda("\n"+attitude)
# else:
#   print("Image did not solve\n")
#   c.send("\nImage did not solve\n")


# c.close()

# print "\n"
