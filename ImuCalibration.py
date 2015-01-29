#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from Utils import Utils

class ImuCalibration(object):
    """docstring for ImuCalibration"""
    def __init__(self):
        super(ImuCalibration, self).__init__()

        # just define necessary values
        # the simulated sensors will use this values to add measurement noise

        # in m/s2 
        self.accel_scale = 1.0
        self.accel_x_bias = 0
        self.accel_x_variance = (0.02) ** 2 # einfach mal so angenommen...

        # in rad / s
        self.gyro_scale = 1.0
        self.gyro_z_bias = 0
        self.gyro_z_variance = (0.1*Utils.d2r) ** 2 # std=1 rad/s - einfach mal so angenommen...

        # in rad
        self.mag_scale = 1.0
        self.mag_offset = 0
        self.mag_theta_variance = (0.1 * Utils.d2r) ** 2 # std=5°

        # in m/s
        self.odometer_variance = (0.02) ** 2

    @classmethod
    def AddNoise(CLS, calib):
        noised = ImuCalibration()
        # in m/s2 
        noised.accel_scale = calib.accel_scale + Utils.add_noise(0, (0.05)**2)
        noised.accel_x_bias = calib.accel_x_bias + Utils.add_noise(0, (0.05)**2)
        noised.accel_x_variance = calib.accel_x_variance + abs(Utils.add_noise(0, (0.1)**2))

        # in rad / s
        noised.gyro_scale = calib.gyro_scale + Utils.add_noise(0, (0.05)**2)
        noised.gyro_z_bias = calib.gyro_z_bias + Utils.add_noise(0, (0.05)**2)
        noised.gyro_z_variance = calib.gyro_z_variance + abs(Utils.add_noise(0, (0.1*Utils.d2r)**2))

        # in rad
        noised.mag_scale = calib.mag_scale + Utils.add_noise(0, (0.05)**2)
        noised.mag_offset = calib.mag_offset + Utils.add_noise(0, (0.05)**2)
        noised.mag_theta_variance = calib.mag_theta_variance + abs(Utils.add_noise(0, (1*Utils.d2r)**2))

        # in m/s
        noised.odometer_variance =calib.odometer_variance + abs(Utils.add_noise(0, (0.1)**2))

        return noised