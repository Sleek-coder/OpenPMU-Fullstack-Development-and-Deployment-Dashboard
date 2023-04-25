"""
OpenPMU - Phasor Estimator
Copyright (C) 2021  www.OpenPMU.org

Licensed under GPLv3.  See __init__.py
"""

from __future__ import print_function
import numpy as np
import os
from estimation.method.Base import EstimationMethodBase

__author__ = 'Xiaodong'

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
print("SCRIPT_DIRECTORY", SCRIPT_DIRECTORY)


class LeastSquare(EstimationMethodBase):
    """
    A least square method.
    Estimate frequency and phasor using least square method offline.
    It will depend on its previous calls.
    All the least square matrices are calculated offline, so a frequency range would be needed beforehand.
    If estimation frequency is 50 Hz, signal frequency is 50Hz, then the range is 25-75 Hz without overlapping.
    If estimation frequency is 100 Hz, signal frequency is 50 Hz, then the range is 0-100 Hz without overlapping, with phase difference unwrap to [-2pi,0],
    but the lower frequencies will cause estimation error (say 5 Hz).
    
    :param harmonicsNo:  number of harmonics to include, base frequency and DC do not count
    :param Fs: sampling frequency
    :param sampleLen: data length of each sample
    :param minFre: frequency range and accuracy for calculation
    :param maxFre:
    :param epsFre: frequency accuracy to stop itration and cache offline
    :param maxStep: maximum iteration
    :return:
    """
    isInvACached = False
    pinvARow1 = None
    pinvARow2 = None

    def __init__(self, harmonicsNo, Fs, sampleLen, baseFre=50, minFre=25, maxFre=75, epsFre=0.001, maxStep=10):
        # read params
        self.harmonicsNo = harmonicsNo
        self.Fs = Fs
        self.epsFre = epsFre
        self.minFre = minFre
        self.maxFre = maxFre
        self.maxStep = maxStep
        self.sampleLen = sampleLen  # sampling size

        self.estFreq = self.Fs / self.sampleLen  # this is the estimation frequency
        self.frequency = baseFre  # calculated frequency
        if self.estFreq > baseFre:
            self.unwrapCenter = -np.pi
        else:
            self.unwrapCenter = 0
        self.prevThetaRad = 0

        m = self.sampleLen // 2   # floor division required as of Python 3
        n = self.harmonicsNo + 1  # plus the base frequency
        grid_m, grid_n = np.mgrid[-m:m:1, 1:n + 1:1]
        coeffA = 2 * np.pi * grid_m * grid_n / self.Fs

        # check if the cache has already been calculated
        if not LeastSquare.isInvACached:
            npzFile = os.path.join(SCRIPT_DIRECTORY, "pinvA.npz")
            sizeInfo = np.array([m, n, minFre, maxFre, epsFre])
            try:
                # load data from file
                data = np.load(npzFile)
                if not (sizeInfo == data["sizeInfo"]).all():
                    raise ValueError
                LeastSquare.pinvARow1 = data["pinvARow1"]
                LeastSquare.pinvARow2 = data["pinvARow2"]

            # if not calculated, do it now
            except (IOError, ValueError, KeyError):
                print("Generating cached matrix, about %.2f Mb of disk space needed." % self.getMemoryUse(sampleLen,
                                                                                                          minFre,
                                                                                                          maxFre,
                                                                                                          epsFre))
                fSize = int((maxFre - minFre) / epsFre)
                LeastSquare.pinvARow1 = np.zeros([fSize, 2 * m], dtype=np.float32)

                # LeastSquare.pinvARow1 = np.zeros([fSize, 2 * m], dtype=np.float) # original code
                LeastSquare.pinvARow2 = np.zeros([fSize, 2 * m], dtype=np.float32)

                # LeastSquare.pinvARow2 = np.zeros([fSize, 2 * m], dtype=np.float)# original code
                A = np.ones((2 * m, n * 2 + 2))
                A[:, -2] = 1
                A[:, -1] = np.arange(-m, m, 1)

                for i in range(fSize):
                    percent = 100.0 * i / fSize
                    print("\r", "-" * int(percent), "-> %%%d" % percent, end="")
                    f = minFre + i * epsFre
                    A[:, 0:-2:2] = np.cos(coeffA * f)
                    A[:, 1:-2:2] = -np.sin(coeffA * f)
                    pinvA = np.linalg.pinv(A)
                    LeastSquare.pinvARow1[i,] = pinvA[0, :]
                    LeastSquare.pinvARow2[i,] = pinvA[1, :]
                print("\r\nSaving matrix to file...", end="")
                np.savez(npzFile, pinvARow1=LeastSquare.pinvARow1, pinvARow2=LeastSquare.pinvARow2, sizeInfo=sizeInfo)
                print("pinInv file has been saved")
                print("done.")
            LeastSquare.isInvACached = True

    def getMemoryUse(self, sampleLen, minFre=25, maxFre=75, epsFre=0.001, ):
        """
        Estimate the disk space needed for the matrix cache for least square offline calculation.

        :param sampleLen: the length of samples for each estimation
        :param minFre: minimum frequency can be estimated
        :param maxFre: maximum frequency can be estimated
        :param epsFre: frequency accuracy to stop itration and cache offline
        :return: space needed in Mb
        """
        fSize = int((maxFre - minFre) / epsFre)
        return np.array([1.0], dtype=np.float32).nbytes * sampleLen * 2 * fSize / 1024 / 1024

        # return np.array([1.0], dtype=np.float).nbytes * sampleLen * 2 * fSize / 1024 / 1024 #original code 

    def getPhasor(self, samples):
        """
        Calculate the frequency and phase angle
        
        :param samples: sampled data
        :return: [mag,frequency, phase angle, rocof]
        :error: the calculated frequency is outside the cached data
        """
        step = 0
        while True:
            step += 1

            # least square
            les = [0, 0]
            if self.frequency <= self.minFre:
                f = self.frequency
                self.frequency = (self.maxFre + self.minFre) / 2
                raise IndexError("Frequency %f smaller than selected boundary %f" % (f, self.minFre))
                # print("Frequency %f smaller than selected boundary %f" % (f, self.minFre))
            elif self.frequency >= self.maxFre:
                f = self.frequency
                self.frequency = (self.maxFre + self.minFre) / 2
                raise IndexError("Frequency %f larger than selected boundary %f" % (f, self.maxFre))
                # print("Frequency %f larger than selected boundary %f" % (f, self.maxFre))
            pos = int((self.frequency - self.minFre) / self.epsFre)
            les[0] = np.dot(LeastSquare.pinvARow1[pos, :], samples)
            les[1] = np.dot(LeastSquare.pinvARow2[pos, :], samples)

            # calculate phase angle
            thetaRad = np.arctan2(les[1], les[0])

            # convert phase difference to [self.unwrapCenter-pi,self.unwrapCenter+pi]
            thetaChange = np.unwrap([self.unwrapCenter, thetaRad - self.prevThetaRad])[1]

            # calculate frequency
            fre = (thetaChange / 2 / np.pi + 1) * self.estFreq

            # check for stop condition
            if np.abs(self.frequency - fre) < self.epsFre or step >= self.maxStep:
                self.prevThetaRad = thetaRad
                rocof = (fre - self.frequency) * self.estFreq
                self.frequency = fre
                # magnitude
                mag = np.sqrt(np.sum(np.power(les, 2)))
                return mag, fre, np.degrees(thetaRad), rocof
            else:
                self.frequency = fre
