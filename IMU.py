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

        # used to generate simulated sensor values
        self.calibration = ImuCalibration()

        # for use in INS, the noise comes from incorrect calibration that ALWAYS happens
        self.calibration_noise = ImuCalibration.AddNoise(self.calibration)

    def get_accel_sample(self):
        return self.calibration.accel_scale * \
                 Utils.add_noise(
                    self.car.ax_local + self.calibration.accel_x_bias, 
                    self.calibration.accel_x_variance)

    def get_odometer_sample(self):
        return Utils.add_noise(
                    self.car.speed, 
                    self.calibration.odometer_variance)

    def get_gyro_sample(self):
        return self.calibration.gyro_scale * \
                 Utils.add_noise(
                    self.car.gyro + self.calibration.gyro_z_bias, 
                    self.calibration.gyro_z_variance)

    def get_mag_sample(self):
        theta_sample = self.calibration.mag_scale * Utils.add_noise(
                            self.car.theta + self.calibration.mag_offset, 
                            self.calibration.mag_theta_variance)
        return math.cos(theta_sample),math.sin(theta_sample),theta_sample

    def get_sensor_array(self):
        # Z contains data for ['accel','odometer','gyro','mag_x', 'mag_y']
        #                       0       1          2      3        4
        mag_x,mag_y,_ = self.get_mag_sample()
        Z = np.array([
                self.get_accel_sample(),
                self.get_odometer_sample(),
                self.get_gyro_sample(),
                mag_x,
                mag_y
            ])
        return Z


