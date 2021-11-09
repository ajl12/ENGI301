# Stress Buddy

The following repository contains files required to operate the Stress Buddy device created using a PocketBeagle.

For more information on how to build the device and connect hardware, visit: https://www.hackster.io/ajl12/stress-buddy-12f85d

# Initializing the PocketBeagle

To initialize the PocketBeagle, perform the following commands in the terminal:

1. sudo apt-get update
2. sudo apt-get install build-essential python-dev python-setuptools python-smbus -y
3. git clone https://github.com/adafruit/adafruit-beaglebone-io-python

# Code

To setup the code, pull the following repository from GitHub: https://github.com/ajl12/ENGI301

In the project_1 folder, 3 files are required to run the device. 

1. The configure_pins.sh file should be used by running the following command in the LINUX terminal:

	chmod 755 configure_pins.sh run

2. The project_1.py file contains the main code for running the device. 

3. The run file is needed to start the device. When ready to run the device, change directories  to var/lib/cloud9/ENGI301/project_1 and type the ./run command into the terminal. 

	Note: The run file also includes a python path to reference the ht16k33.py files under var/lib/cloud9/ENGI301/python







