If you need to set up a new raspberry pi, follow the setup instructions in the User Guide section 2 (Star Tracker Setup)

Below is a guide for some of the software you will need to download:
- Connect the raspberry pi to the internet using whatever means you want (wifi, ethernet, bridged connection to laptop, shared internet connection with phone)
- Open up a command terminal window and type the following commands:
	sudo apt install python
	sudo apt-get update
	sudo apt install python-pip
	sudo apt-get install python-opencv
	sudo apt install swig
	pip install pyserial (for serial connections)
- Recompile the C code by running the following command:
	./unit_test.sh -r Indoor_test_pointing
	[This command must be run from the tests folder (or whatever folder unit_test.sh is in).
	If you get “permission denied” run the command ‘sudo chmod +x unit_test.sh’]
- Run the following commands to set up for calibration
	sudo apt-get install git libvte-dev libtool ctags gdb meld nemiver libwebkitgtk-dev vim geany geany-plugins astrometry.net python-astropy
	sudo apt-get install python-scipy libopencv-dev python-opencv swig
	cd /usr/share/astrometry (Run below commands within this directory)
		sudo wget http://data.astrometry.net/4100/index-4112.fits
		sudo wget http://data.astrometry.net/4100/index-4113.fits
		sudo wget http://data.astrometry.net/4100/index-4114.fits
		sudo wget http://data.astrometry.net/4100/index-4115.fits
		sudo wget http://data.astrometry.net/4100/index-4116.fits
		sudo wget http://data.astrometry.net/4100/index-4117.fits
		sudo wget http://data.astrometry.net/4100/index-4118.fits
		sudo wget http://data.astrometry.net/4100/index-4119.fits

