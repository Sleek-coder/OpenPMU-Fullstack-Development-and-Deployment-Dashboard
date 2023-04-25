"""
OpenPMU - Phasor Estimator
Copyright (C) 2021  www.OpenPMU.org

Licensed under GPLv3.  See __init__.py
"""

from __future__ import print_function
import numpy as np
from estimation.method.Base import EstimationMethodBase
__author__ = 'Xiaodong'


class LeastSquare(EstimationMethodBase):
    """
    An online least square method.
    Estimate frequency and phasor using least square method online caculation.
    The class should be instanced and called using data from the signal.
    getFrePhase method will depend on its previous calls,
    because the least square matrix is solved online, it would take a long time for each estimation.

    :param harmonicsNo:  number of harmonics to include, base frequency and DC do not count
    :param Fs: sampling frequency
    :param sampleLen: data length of each sample
    :param epsFre: frequency accuracy to stop itration
    :param maxStep: maximum iteration
    :return:
        """
    def __init__(self, harmonicsNo, Fs, sampleLen, baseFre=50, minFre=25,maxFre=75, epsFre=0.001, maxStep=10):

        self.harmonicsNo = harmonicsNo
        self.Fs = Fs
        self.epsFre = epsFre
        self.maxStep = maxStep
        self.sampleLen = sampleLen  # sampling size

        self.coeffA = None  # matrix A coefficients
        self.pinvA = None  # A inverse
        self.matrixA = None
        self.estFreq = self.Fs / self.sampleLen  # this is the estimation frequency
        self.frequency = baseFre  # calculated frequency
        if self.estFreq>baseFre:
            self.unwrapCenter=-np.pi
        else:
            self.unwrapCenter=0
        self.prevThetaRad = 0

        m = self.sampleLen / 2
        n = self.harmonicsNo + 1  # plus the base frequency
        grid_m, grid_n = np.mgrid[-m:m:1, 1:n + 1:1]
        self.coeffA = 2 * np.pi * grid_m * grid_n / self.Fs
        self.matrixA = np.ones((2 * m, n * 2 + 2))
        self.matrixA[:, -2] = 1
        self.matrixA[:, -1] = np.arange(-m, m, 1)
        self.matrixA[:, 0:-2:2] = np.cos(self.coeffA * self.frequency)
        self.matrixA[:, 1:-2:2] = -np.sin(self.coeffA * self.frequency)
        self.pinvA = np.linalg.pinv(self.matrixA)

    def getPhasor(self, samples):
        """
        Calculate the frequency and phase angle
        
        :param samples: sampled data
        :return: [mag,frequency, phase angle, rocof]
        """
        step = 0
        while True:
            step += 1

            # least square
            les = np.dot(self.pinvA, samples)

            # calculate phase angle
            thetaRad = np.arctan2(les[1], les[0])

            # convert phase difference to [self.unwrapCenter-pi,self.unwrapCenter+pi]
            thetaChange = np.unwrap([self.unwrapCenter, thetaRad - self.prevThetaRad])[1]

            # calculate frequency
            fre = (thetaChange/2/np.pi+1)*self.estFreq

            # check for stop condition
            if np.abs(self.frequency - fre) < self.epsFre or step >= self.maxStep:
                self.prevThetaRad = thetaRad
                rocof=(fre-self.frequency)*self.estFreq
                self.frequency = fre
                mag=np.sqrt(np.sum(np.power(les,2)))
                return mag,fre, np.degrees(thetaRad), rocof
            else:
                self.frequency = fre
                self.matrixA[:, 0:-2:2] = np.cos(self.coeffA * fre)
                self.matrixA[:, 1:-2:2] = -np.sin(self.coeffA * fre)
                self.pinvA = np.linalg.pinv(self.matrixA)
