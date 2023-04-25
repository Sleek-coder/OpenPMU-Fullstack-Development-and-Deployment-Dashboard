 30823# -*- coding: utf-8 -*-
"""
OpenPMU - CSVlogger
Copyright (C) 2022  www.OpenPMU.org

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

from threading import Thread, Event
from queue import Queue
from datetime import datetime, timedelta
import json
import signal
import os
import time
import glob, shutil
# import csv

import UDPphasor
# import UDP
import socket

# ###################################
# ------------- Threads -------------

# First function is threaded and puts received phasors into a queue
# Second function is called by main programme to get phasors from queue

def get_Phasor(queue_out, IP, Port):
    
    global stopThread
    
    # Set up an instance of the PMU Phasor Value receiver
    pmu = UDPphasor.Receiver(IP, Port)
    while not stopThread: 
        try:
            dataInfo = pmu.receive()    # Receive the latest frame of Phasor Values from the ADC.
           
        except:
            continue
        
        if dataInfo is None:        # If there's no frame of data, skip rest of loop and wait for next frame.
            continue
        
        dataInfo2 = dataInfo.copy()
        # print("dataInfo2",dataInfo2) 

        queue_out.put(dataInfo2)
        
def get_queue(queue_in):
         
    if not queue_in.empty():
        data = queue_in.get()
        data2 = data.copy()
    else:
        data2 = None
    
    return(data2)


# ###################################
# ------------ Functions ------------
        
# Keyboard Interrupt event handler (CTRL+C to quit)
def signal_handler(signal, frame):
    
    global stopThread
    
    stopThread = True
    print('You pressed Ctrl+C!')
    time.sleep(1)
    # pmu.close()
    # sys.exit(0)
    
# Load the config file    
def loadConfig(configFile="config.json"):
    with open(configFile) as jsonFile:
        return json.load(jsonFile)
    
# Covert OpenPMU ADC stream date/time to Python datetime object
def getPMUdatetime(dataInfo):
    return datetime.combine(datetime.strptime(dataInfo['Date'], "%Y-%m-%d").date(), datetime.strptime(dataInfo['Time'], "%H:%M:%S.%f").time())

# Covert the dictionary into a single, flat line of phasor values
# --- format is "Date,Time,Frame,<phKeys>*<phChannels>"
def makeCSVline(phDict, phChannels=[], precision=3, phKeys=["Mag", "Angle", "Freq", "ROCOF"]): 
        
    if len(phChannels) == 0:
        phChannels = list(range(phDict["Channels"]))
        print("phChannels",phChannels)
      
    # Get the datetime of the Phasor, format as ISO time
    phTime  = getPMUdatetime(phDict)
    timeISO = phTime.astimezone().isoformat('T', 'milliseconds')
    
    ExcelDate = str(phTime.date())
    ExcelTime = str(phTime.time())
        
    # CSV Line
    csvLine = str()                                     # Start new line
    csvLine += ExcelDate + "," + ExcelTime + ","        # Add Excel friendly format datetime
    csvLine += str(int(phDict["Frame"] / 2)) +","       # Add phasor frame number (0 = top of second)
    
    # Convert phasor dictionary into strings, append to CSV line  
    for i in phChannels:

        phLine = str()
        
        for key in phKeys:
            
            formatStr = ("{:." + str(precision) + "f}")        
            phLine += formatStr.format(phDict["Channel_%d" % i][key]) + ","
        
        csvLine += phLine
        
    csvLine = csvLine.rsplit(',',1)[0]                  # Remove trailing comma 
    # print("I got into the CSVLine maker!!!")
    
    return csvLine

# Makes the header for a new CSV file
def makeCSVheader(phChannels=[], phKeys=["Mag", "Angle", "Freq", "ROCOF"]):
    
    if len(phChannels) == 0:
        phChannels = list(range(phDict["Channels"]))
    
    header = str()
    header = 'Date,Time,Frame,'                     # Add initial fields
    
    for i in phChannels:                            # Loop phasor fields
        for key in phKeys:            
            header += key + str(i) + ','            # Add channel number to key 
            # print("I got into the CVSVheader maker")         
    return header.rsplit(',',1)[0]                  # Remove trailing comma

# Finds the floor datetime for a given interval, used to create CSV filenames
def floorTime(timeIn, interval):

    floorTime = timeIn - timedelta(minutes=timeIn.minute % interval,
                                 seconds=timeIn.second,
                                 microseconds=timeIn.microsecond)
    return floorTime

# Ensure the path to the wavefile exists, if not create the path         
def ensureDir(filePath):
    directory = os.path.dirname(filePath)
    if not os.path.exists(directory):
        os.makedirs(directory) 
        
# Generate CSV file path        
def makeCSVFilePath(csvFileTime, csvPathRoot):        
    csvPathYMD = csvFileTime.strftime("%Y-%m-%d") + "/"        
    csvFileName = str(csvFileTime)[0:19].replace(':','-').replace(' ','_') + '.csv'
    csvFilePath = csvPathRoot + csvPathYMD + csvFileName
    return csvFilePath
        
# Prints the header bar for the CLI progress ticker       
def printProgressHeader(csvTime, frameTime):
    print("CSV file time:", str(csvTime), "- Now:", str(frameTime.time()))
    print('0.........1.........2.........3.........4.........5.........|')

# Delete old records
def deleteOldRecords(filePath, daysToKeep, dateNow):
    
    deleteEpoch = dateNow.date() - timedelta(days=daysToKeep)
    
    print(dateNow, deleteEpoch)    
    
    for path in glob.glob(filePath + "*"):
        
        try:
            dateStr = path.split('/')[-1]
            date = datetime.strptime(dateStr, "%Y-%m-%d").date()
        except:
            date = datetime.strptime("3000-01-01", "%Y-%m-%d").date()
        
        if date < deleteEpoch:
            shutil.rmtree(path)
            print(path, "--- Path deleted")
        else:
            print(path, " --- Path retained")        



#added by me 
# def parseToCSV(data):
#     with open('test3.csv', 'w') as csvfile:
#         print("I am printing to csv")
#         # print("list(data[0].keys()", list(data[0].keys()))
#         writer = csv.DictWriter(csvfile, fieldnames = list(data[0].keys()))
#         writer.writeheader()
#         writer.writerows(data)
    
# ####################################
# --------------- MAIN ---------------

if __name__ == '__main__':
    
    # Keyboard interrupt handler
    signal.signal(signal.SIGINT, signal_handler)

    print("OpenPMU Phasor Logger")
    
    config = loadConfig("config.json")
    
    phasorQueue = Queue(3000)    
    t = Thread(target=get_Phasor, args=(phasorQueue, config["recvIP"], config["recvPort"]))
    t.start()
    
    # Initialise variables required in loop
    csvBuffer           = str()
    csvWriteBuffer      = str()
    csvFileTimeInUse    = datetime.fromisoformat("1955-11-12T22:04:00")
    frameTime           = datetime.fromisoformat("1955-11-12T22:04:00")
    
    firstLoop = True
    stopThread = False
    while not stopThread:
        
        dataInfo = get_queue(phasorQueue)       # Receive the latest frame of Phasor Values from the ADC.
        if dataInfo is None:                    # If there's no frame of data, skip rest of loop and wait for next frame.
           time.sleep(0.005)
           continue

        # Calculate frame time as Python datetime object
        preFrameTime = frameTime                # Set Previous Frame Time first
        frameTime    = getPMUdatetime(dataInfo)
        
        # Get CSV file time as the floor of the current time and csvInterval
        # csvInterval - Minutes between CSV files, starting at top of the hour        
        csvFileTime = floorTime(frameTime, config["csvInterval"])
        
        if firstLoop == True:
            firstLoop = False
            # Print progress bar header
            printProgressHeader(csvFileTime, frameTime)
            for i in range(frameTime.second):
                print('-', end='')             
            
            continue    # Now that initialisation is complete, restart loop


        
        # Check for second rollover, copy csvBuffer to csvWriteBuffer
        if frameTime.microsecond < preFrameTime.microsecond:
                                    
            csvWriteBuffer += csvBuffer
            
            csvBuffer = str()
            
            # Progress Bar
            # This updates the console with a tick each second based on received frameTime        
            if ( (frameTime.second - 1) % 10) == 0:
                print('|', end='', flush=True)
            else:
                print('.', end='', flush=True)
                
                
        # Check for minute rollover, write buffer to csvFile
        if frameTime.minute != preFrameTime.minute:            
            
            csvFilePath = makeCSVFilePath(csvFileTimeInUse, config["csvPath"])
            ensureDir(csvFilePath)                  # Make sure directory for CSV file exists
            print("The csv filepath is", csvFilePath)
            with open(csvFilePath, 'a') as f:
                print("Your csv is about to be written")
                f.write(csvWriteBuffer) 
                print("This is the content in your csvWriteBuffer", csvWriteBuffer)   
            csvWriteBuffer = str()                              # Clear csvWriteBuffer
        
            print('')                                           # Add a line break
            printProgressHeader(csvFileTime, frameTime)         # Print heartbeat debug info 
     

        # Initialise a new CSV file with header
        if csvFileTime != csvFileTimeInUse:
                        
            header = makeCSVheader(config["csvChannels"])
            
            csvFilePath = makeCSVFilePath(csvFileTime, config["csvPath"])
            ensureDir(csvFilePath)                  # Make sure directory for CSV file exists
            
            with open(csvFilePath, 'a') as f:
                f.write(header + '\n')
                
            csvFileTimeInUse = csvFileTime        
        
        # Check for day rollover (i.e. midnight)
        if frameTime.day != preFrameTime.day:                
            if config["allowDeletion"]:
                print("Deleting records older than %d days" % (config["daysToKeep"]))
                deleteOldRecords(config["csvPath"], config["daysToKeep"], frameTime)
        
        # 1 Second Buffer
        csvLine = makeCSVline(dataInfo, config["csvChannels"])  # Make one line of the CSV file using present phasor 
        csvBuffer += csvLine + "\n"                             # Append to buffer which is copied to csvWriteBuffer each second
        
         
    t.join()    # Join thread, wait for it to terminate
    print("End of programme. Exiting!")    

    # parseToCSV(dataInfo)
    #parse in your data
    # print("mydata", mydata)
    