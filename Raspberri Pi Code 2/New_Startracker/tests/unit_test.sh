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
	# 'mode' 'num of cropped stars' 'seial connection (bool) [for testing]' 'take picture? (bool) [for testing]' 'crop images (bool) [for testing]'
	
	# values for testing are hardcoded below (NOT PASSED IN).  
	num_stars="$2" # second argument
	
	#time python2.7 client_test2.py $TESTDIR/res480480 $TESTDIR/calibration.txt 1991.25 $TESTDIR/median_image.png $TESTDIR/stars.txt track 5 || exit # serial connection
	time python2.7 client_test2.py $TESTDIR/res480480 $TESTDIR/calibration.txt 1991.25 $TESTDIR/median_image.png $TESTDIR/stars.txt \
	track $num_stars 0 0 0|| exit
fi

if [[ $CALIBRATECAL == 1 ]]; then
	time python2.7 cal.py $TESTDIR || exit
fi

if [[ $IMG_TEST == 1 ]]; then
	#time python2.7 client_test2.py $TESTDIR/res480480 $TESTDIR/calibration.txt 1991.25 $TESTDIR/median_image.png $TESTDIR/stars.txt lis 5 || exit
	#python2.7 startracker.py $TESTDIR/calibration.txt 1991.25 $TESTDIR/median_image.png
	#xfce4-terminal --tab --execute python2.7  client.py
	
	num_stars="$2"
	
	#time python2.7 'code being run' 'directory of stars' 'calibration text' 'year' 'median image' 'star text file'
	# 'mode' 'num of cropped stars' 'seial connection (bool) [for testing]' 'take picture? (bool) [for testing]' 'crop images (bool) [for testing]'
	time python2.7 client_test2.py $TESTDIR/res480480 $TESTDIR/calibration.txt 1991.25 $TESTDIR/median_image.png $TESTDIR/stars.txt \
	track $num_stars 0 0 0|| exit
fi

#if [[ $TRACK == 1 ]]; then
#	python2.7 star_track_mode.py $TESTDIR/calibration.txt 1991.25 $TESTDIR/median_image.png
#	#xfce4-terminal --tab --execute python2.7  client.py
#fi

if [ "$KILLPID" != "" ] ; then 
	kill $KILLPID
fi

popd>/dev/null
