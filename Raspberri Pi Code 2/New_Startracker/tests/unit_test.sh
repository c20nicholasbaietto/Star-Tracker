#!/bin/bash

#CALIBRATE=0
CLIENT_TEST=0
CALIBRATECAL=0
IMG_TEST=0
RECOMPILE=0

while getopts ":citr" opt; do
  case $opt in
    c)
	  CALIBRATECAL=1
      ;;
    i)
	  IMG_TEST=1
      ;;
    t)
	  CLIENT_TEST=1
      ;;
    r)
	  RECOMPILE=1
      ;;
   \?)
      echo "Usage: ./unit_test.sh [options] testdir [cmd]"
      echo -e ""
      echo -e "\t-c\tCalibrate camera"
      echo -e "\t-t\tRun tracking mode"
      echo -e "\t-i\tRun lost in space mode"
      echo -e "\t-r\tRecompile the backend"
      exit
      ;;
  esac
done
shift "$[$OPTIND-1]"

pushd "`dirname $0`">/dev/null

TESTDIR="$1"
if [ ! -d "$TESTDIR" ]; then
	echo "'$TESTDIR' is not a valid directory "
	exit
fi

NUM_STARS="$2" # number of stars cropped in tracking mode
SERIAL="$3" # are you sending data back over a serial connection? (1 = yes, 0 = no)
TAKE_PIC=0 # are you using the camera to take pictures? (1 = yes, 0 = no)
CROP=1 # are you cropping images for tracking mode? (1 = yes, 0 = no)

shift

KILLPID=""
if [[ $RECOMPILE == 1 ]]; then
	pushd beast >/dev/null
	./go || exit
	popd>/dev/null
fi

#if [[ $CALIBRATE == 1 ]]; then
#	time python2.7 calibrate_old.py $TESTDIR || exit
#fi

if [[ $CLIENT_TEST == 1 ]]; then
	#time python2.7 'code being run' 'directory of stars' 'calibration text' 'year' 'median image' 'star text file'
	# 'mode' 'num of cropped stars' 'seial connection' 'take pictures' 'crop image'
	
	time python2.7 client_test2.py $TESTDIR/res480480 $TESTDIR/calibration_copy.txt 1991.25 $TESTDIR/median_image_copy.png \
	track $NUM_STARS $SERIAL $TAKE_PIC $CROP || exit
fi

if [[ $CALIBRATECAL == 1 ]]; then
	#time python2.7 'code being run' 'directory for calibration' 'take pictures'
	time python2.7 cal.py $TESTDIR $TAKE_PIC || exit
fi

if [[ $IMG_TEST == 1 ]]; then
	#time python2.7 'code being run' 'directory of stars' 'calibration text' 'year' 'median image' 'star text file'
	# 'mode' 'num of cropped stars' 'seial connection' 'take pictures' 'crop image (always 0 for lis)'
	
	time python2.7 client_test2.py $TESTDIR/res480480 $TESTDIR/calibration.txt 1991.25 $TESTDIR/median_image.png \
	lis $NUM_STARS $SERIAL $TAKE_PIC 0 || exit
fi

#if [[ $TRACK == 1 ]]; then
#	python2.7 star_track_mode.py $TESTDIR/calibration.txt 1991.25 $TESTDIR/median_image.png
#	#xfce4-terminal --tab --execute python2.7  client.py
#fi

if [ "$KILLPID" != "" ] ; then 
	kill $KILLPID
fi

popd>/dev/null
