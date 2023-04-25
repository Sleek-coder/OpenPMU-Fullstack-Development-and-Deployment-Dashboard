"""
OpenPMU - Phasor Estimator
Copyright (C) 2021  www.OpenPMU.org

Licensed under GPLv3.  See __init__.py
"""

from __future__ import print_function

import numpy as np
import threading
from ..interface.PMU import Receiver
from ..interface.UDP import Sender
import json

__author__ = 'Xiaodong & Team OpenPMU'


class EstimationMethodBase:
    """
    Base class for a phasor estimation method. 
    Use this class to implement custom estimation methods such as LeastSquare. 
    
    """

    def __init__(self, ):
        pass

    def getPhasor(self, samples):
        """
        Calculate the frequency and phase angle. 
        This method should return the calculated result before next call, typically 10ms or 20ms. 
        
        :param samples: sampled data list
        :return: [mag,frequency, phase angle, rocof]
        :error: the calculated frequency is outside the method's capacity.
        """


class EstimatorBase:
    """
    Base class for a phasor estimation instance, 
    which receives data from PMU, depack data, then pass data to phasor etimation method. 
    Use this as base class and override estimationMethod to choose different phasor estimation method, 
    then call run to start phasor estimation. 
    
    :param receiveIP: PMU data into address
    :param receivePort:  PMU data port
    :param sendIP: estimated phasor outward address
    :param sendPort: estimated phasor outward port
    :return: None
    """

    def __init__(self, receiveIP, receivePort, sendIP, sendPort):
        """
        
        """
        self.estimationFrequency = 50  # Hz
        self.receiveIP = receiveIP
        self.receivePort = receivePort
        self.sendIP = sendIP
        self.sendPort = sendPort

        self.estimationThread = threading.Thread(target=self.run)
        self.estimationThread.daemon = True
        self.runThreadEvent = threading.Event()
        # default start the thread
        # self.runThreadEvent.set()
        # self.estimationThread.start()

    def estimationMethod(self, Fs, sampleLen):
        """
        Return a custom phasor estimation method instance inherited from EstimationMethodBase
        :param Fs: sampling frequency
        :param sampleLen: each sample length for estimation
        :return: an object instance of the estimation method
        """    
        raise NotImplementedError("Please implement estimationMethod")

    def oneChannelDone(self, date, time, chNo, mag, frequency, angle, rocof):
        phbuffer = {}
        """
        Finished estimation of one channel
        
        :param frequency: estimated frequency
        :param angle: estimated phase angle
        :return: None
        """
        phasorRowList = []
        phDict = {}
        flag = chNo
        phDict['date'] = date
        phDict['time'] = time
        phDict['chNo'] = chNo
        mag = round(mag, 4)
        phDict['mag'] = mag
        frequency = round(frequency, 2)
        phDict['frequency'] = frequency
        angle = round(angle, 2)

        phDict['angle'] = angle
        rocof = round(rocof, 2)
        phDict['rocof'] = rocof
        # phasorList.append(phDict)

        # Prints the estimated synchrophasors to the console      
        # print("a single phasor is dict is here!!", phDict)
        print("\t%s \t%s \t%d \t%.4f \t%.2f \t%8.2f \t%6.2f" % (date, time, chNo, mag, frequency, angle, rocof))
        # phbuffer  += phDict
        # print(phbuffer)
        # with open('my_dict.json', 'w') as f:
        #     json.dump(phDict, f)
        # phasorRowList.append(phDict)
        # print("phasorRowList", phasorRowList)



    def stop(self, ):
        """
        Stop the estimation. 
        This method will stop the phasor estimation after the current data is processed. 
        """
        self.runThreadEvent.clear()
        self.estimationThread.join()

    def start(self, ):
        """
        Start the estimation.
        """
        self.runThreadEvent.set()
        if not self.estimationThread.is_alive():
            self.estimationThread = threading.Thread(target=self.run)
            self.estimationThread.start()


    def run(self, ):
        """
        Run the estimation and send phasor. This function runs in a thread.
        This will read data from the network, run the phasor estimation and send the data out via network.

        :return: None
        """
        timeout = 1
        pmuReceiver = Receiver(self.receiveIP, self.receivePort, False)
        sender = Sender(self.sendIP, self.sendPort)

        chEstimation = None
        payloadDataBuffer = None
        dataCnt = 0
        while self.runThreadEvent.isSet():
            try:
                phasor = pmuReceiver.receive(timeout)
                if phasor is None:  # timeout
                    print("Receiving data from PMU timed out.") 
                    continue

                # get some basic information
                chNo = phasor["Channels"]
                Fs = phasor["Fs"]
                n = phasor['n']
                date = phasor["Date"]
                time = phasor["Time"]
                frame = phasor["Frame"]
                interval = phasor['n'] * 1000.0 / phasor['Fs']
                recNo = int(1000.0 / self.estimationFrequency / interval)

                # create phasor estimation for each channel
                if chEstimation is None:
                    chEstimation = []
                    for i in range(chNo):
                        chEstimation.append(self.estimationMethod(Fs, n * recNo))
                    # hold data to estimation
                    payloadDataBuffer = np.zeros([chNo, n * recNo])
                    continue

                # Ensure that the synchrophasors are always based on "top of the second", i.e. 0.000, 0.020, 0.040, not 0.010, 0.030, 0.050
                if frame == 0:
                    dataCnt = 1

                # read sampled data
                for i in range(0, chNo):
                    k = 'Channel_%d' % i
                    try:
                        payloadDataBuffer[i, dataCnt * n:(dataCnt * n + n)] = (phasor[k]['Payload'])
                        del phasor[k]['Payload']
                    except KeyError:
                        print("%s payload missing" % k)

                dataCnt += 1
                                                   
                #  estimate
                if dataCnt >= recNo:
                    dataCnt = 0
                    for i in range(0, chNo):
                        try:
                            mag, frequency, angle, rocof = chEstimation[i].getPhasor(payloadDataBuffer[i,])
                        except IndexError as e:
                            print(e)
                            frequency = 0
                            angle = 0
                            mag = 0
                        k = 'Channel_%d' % i
                        phasor[k]["Freq"] = frequency
                        phasor[k]["Angle"] = angle
                        phasor[k]["Mag"] = mag
                        phasor[k]["ROCOF"] = rocof
                        
                        self.oneChannelDone(date, time, i, mag, frequency, angle, rocof)
                        
                        # For debug, operate on only first channel
                        # if i == 0:
                            # self.oneChannelDone(date, time, i, mag, frequency, angle, rocof)

                    # send out phasor
                    # print("phasor abt to send", phasor)
                    sender.send(phasor)
                
            except KeyboardInterrupt:
                self.stop()

        pmuReceiver.close()
