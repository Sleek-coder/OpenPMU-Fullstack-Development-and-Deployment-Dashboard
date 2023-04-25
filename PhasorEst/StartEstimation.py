"""
OpenPMU - Phasor Estimator
Copyright (C) 2021  www.OpenPMU.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from estimation.method.Base import EstimatorBase
from estimation.method.LeastSquareOffline import LeastSquare as LeastSquareOffLine
from estimation.method.LeastSquareOnline import LeastSquare as LeastSquareOnline
from estimation.interface.tools import getLocalIP
#from SimpleXMLRPCServer import SimpleXMLRPCServer
import json
import signal, sys		# Needed for CTRL+C to stop programme!
import time				# For having a sleep!



# Original code Xiaodong 2015/16
# Updates since by OpenPMU Admin
# Copyright 2021, OpenPMU Admin

__author__ = 'Xiaodong & OpenPMU Admin'

# This script estimates phasors from a stream of XML/UDP sampled values (SV).
# The phasors are send onwards via XML/UDP.
# Configuration is stored in config.json.


## ---------- This is a list of the available Phasor Estimators ----------
## -----------------------------------------------------------------------

# ------------------------------------------all the available estimation methods (classes)------------------------------
# to add new methods, inherit from EstimationMethodBase and create a new lambda here (with two params Fs and sampleLen)
estimationMethodList = {
    # Note - harmonicsNo excludes fundamental, so e.g. 10 estimates 11th harmonic
    # Note - high epsFre will lead to high memory usage, can cause issues with low memory R Pi models
    "leastsquareoffline": lambda Fs, sampleLen: \
        LeastSquareOffLine(harmonicsNo=10, Fs=Fs, sampleLen=sampleLen, minFre=25, maxFre=75, epsFre=0.001, maxStep=5),
    "leastsquareonline": lambda Fs, sampleLen: \
        LeastSquareOnline(harmonicsNo=0, Fs=Fs, sampleLen=sampleLen, minFre=25, maxFre=75, epsFre=0.001, maxStep=2),
}

## ---------- Functions to Load/Save Configuration from config.json ----------
## ---------------------------------------------------------------------------
config_file = "config.json"

def loadConfig():
    global receiveIP, receivePort, sendIP, sendPort, estimationFrequency, estimationMethod
    try:
        with open(config_file) as j:
            config = json.load(j)
            receiveIP = config["receiveIP"]
            receivePort = config["receivePort"]
            sendIP = config["sendIP"]
            sendPort = config["sendPort"]
            estimationFrequency = config["estimationFrequency"]
            estimationMethod = config["estimationMethod"]
    except Exception as e:
        print(e)


def saveConfig():		# For future use
    with open(config_file, "w") as j:
        json.dump({"receiveIP": receiveIP, "receivePort": receivePort,
                   "sendIP": sendIP, "sendPort": sendPort,
                   "estimationFrequency": estimationFrequency,
                   "estimationMethod": estimationMethod,
                   }, j, indent=4)

## ---------- Setup the Phasor Estimator / Instance of 'EstimatorBase' Class ----------
## ------------------------------------------------------------------------------------				   
				   
def phasorEstimation(receiveIP, receivePort, sendIP, sendPort,
                     estimationFrequency, methodName):
    print('Receiving PMU data at %s:%d' % (receiveIP, receivePort))
    print("Sending phasor result to  %s:%d " % (sendIP, sendPort))
	
    estimation = EstimatorBase(receiveIP, receivePort, sendIP, sendPort)  # estimation is an instance of the EstimatorBase class in estimation/method/Base.py
	
    estimation.estimationFrequency = estimationFrequency
    estimation.estimationMethod = estimationMethodList.get(methodName)

    # Print the header for the console synchrophasor printout ( estimation.oneChannelDone() )
    print("\tDate      \tTime      \tChannel \tMagnitude \tFrequency \tPhase angle \tROCOF")
    print("estimation is ", estimation)
    #saveConfig()		# For future use
    return estimation				   
				   
## ---------- IMPORTANT - Catches CTRL+C to exit ----------
## --------------------------------------------------------				   
def signal_handler(signal, frame):
	print('You pressed Ctrl+C!  Now STOPPING the Estimator and then EXITING.')
	estimation.stop()		# Stop the estimation thread
	time.sleep(1) 			# Give the estimation thread time to stop
	print('Exiting OpenPMU.  Goodbye, see you soon!  :)')
	sys.exit(0)				# Exit the programme

	
	
## ---------- OpenPMU V2 - Estimator - MAIN PROGRAMME ----------
## -------------------------------------------------------------

# Splash screen - everyone loves a splash screen
print("--------------------------------------------------------")
print("Welcome to OpenPMU V2 - Phasor Estimator")
print("www.OpenPMU.org")
print("Copyright 2021, OpenPMU Admin")
print("--------------------------------------------------------")
print("")


# Set default config and then Load Configuration from config.json
IP_list = getLocalIP()
print("Local ip address is %s" % IP_list)		# Useful when there are multiple NICs
print("")
# receiveIP = "127.0.0.1"
receiveIP = "192.168.0.102"
receivePort = 48001
# sendIP ="127.0.0.1"
sendIP = "192.168.0.100"
sendPort = 48003
# sendPort = 48003
estimationFrequency = 50
estimationMethod = "leastsquareoffline"

loadConfig()									# Load config from config.json

# Print configuration
print("---------------------Configuration---------------------")
print("Phasor estimation frequency is:       %d" % estimationFrequency)
print("Phasor estimation method is:          %s" % estimationMethod)
print("Receiving Sampled Values (SV) from:   %s:%d" % (receiveIP, receivePort))
print("Sending phasor result to:             %s:%d" % (sendIP, sendPort))
print("")

# estimation is an instance of the EstimatorBase class in estimation/method/Base.py, setup via function phasorEstimation
estimation = phasorEstimation(receiveIP, receivePort, sendIP, sendPort, estimationFrequency, estimationMethod)			


# Setup the interrupt to catch CTRL+C and stop the programme
signal.signal(signal.SIGINT, signal_handler)

# Start the estimator thread
estimation.start()

# Loop forever
while True:
    time.sleep(1)



