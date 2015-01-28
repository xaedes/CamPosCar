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
        self.imuCalibration.accel_scale = 1.0
        self.imuCalibration.accel_x_bias = 0
        self.imuCalibration.accel_x_variance = (2) ** 2 # einfach mal so angenommen...

        # in rad / s
        self.imuCalibration.gyro_scale = 1.0
        self.imuCalibration.gyro_z_bias = 0
        self.imuCalibration.gyro_z_variance = (1*Utils.d2r) ** 2 # std=1 rad/s - einfach mal so angenommen...

        # in rad
        self.imuCalibration.mag_scale = 1.0
        self.imuCalibration.mag_offset = 0
        self.imuCalibration.mag_theta_variance = (5 * Utils.d2r) ** 2 # std=5°

        # in m/s
        self.imuCalibration.odometer_variance = (2) ** 2
