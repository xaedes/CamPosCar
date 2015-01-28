#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import math
from Draw import Draw
from Utils import Utils
from ImuCalibration import ImuCalibration

class IMU(object):
    """docstring for Car"""
    def __init__(self, car):
        super(IMU, self).__init__()
        self.car = car
        self.calibration = ImuCalibration()

    def get_sensor_array(self):
        # Z contains data for ['accel','odometer','gyro','mag_x', 'mag_y']
        #                       0       1          2      3        4
		Z = np.array([])
		return Z


	def add_noise(self, value, variance):
		return value + np.random.normal(0,math.sqrt(variance))