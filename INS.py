#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import math                        # Mathefunktionen braucht man auch häufiger mal

from Kalman import Kalman
from Utils import Utils # vorkommen nach aufrufen suchen und an aktuelle Utils methoden anpassen

from ImuCalibration import ImuCalibration

class Integrator(object):
    def __init__(self, dt=1):
        super(Integrator, self).__init__()
        self.dt = dt
        self.sum = 0

    def add(self, value, dt=None):
        if dt is not None:
            self.dt = dt
        self.sum += value * self.dt

class WienerKalman(Kalman):
    def __init__(self, dt=0.01, white_noise_scale=1, R=1):
        super(WienerKalman, self).__init__(1,1)
        self.dt = dt
        self.white_noise_scale = white_noise_scale
        self.H[0,0] = 1 
        self.F *= 1 # integration
        self.Q *= self.dt * self.white_noise_scale  
        self.R *= R
        self.P *= 0
    def update_dt(self, dt):
        self.dt = dt
        self.Q = np.matrix(np.identity(1)) * self.dt * self.white_noise_scale


class INS(object):
    # gyro and orientation in rad/s
    sensors = ['accel','odometer','gyro','mag_x', 'mag_y']
    def __init__(self,calib, dt=0.01):
        super(INS, self).__init__()

        # self.imuCalibration = ImuCalibration('/home/xaedes/bags/mit_kamera/magcalib/2014-08-20-17-33-13.bag')
        self.imuCalibration = calib
        
        self.states = ['speed', 'orientation', 'yaw_rate', 'pos_x', 'pos_y']
        self.states = dict(map((lambda x: (x,0)),self.states))

        self.dt = dt

        self.gyro_integrated = Integrator()
        self.accel_integrated = Integrator()

        self.orientation_error = WienerKalman(self.dt, self.imuCalibration.gyro_z_variance, self.imuCalibration.mag_theta_variance)
        self.velocity_error = WienerKalman(self.dt, self.imuCalibration.accel_x_variance, self.imuCalibration.odometer_variance)

        self.vx_integrated = Integrator()
        self.vy_integrated = Integrator()

        self.mag_offset = None
        self.o_error_last = None

    def calibrate_sensors(self, Z):
        Z = Z.copy()
        Z[0] = (Z[0] - self.imuCalibration.accel_x_bias)*self.imuCalibration.accel_scale
        Z[2] = (Z[2] - self.imuCalibration.gyro_z_bias)*self.imuCalibration.gyro_scale
        Z[[3,4]] -= self.imuCalibration.mag_offset
        Z[[3,4]] /= self.imuCalibration.mag_scale       
        return Z

    def update_pose(self, pos_x, pos_y, orientation):
        gain = 1
        self.vx_integrated.sum = gain*pos_x + (1-gain)*self.vx_integrated.sum
        self.vy_integrated.sum = gain*pos_y + (1-gain)*self.vy_integrated.sum
        # self.states['orientation'] = gain*orientation + (1-gain)*self.states['orientation']
        # self.gyro_integrated.sum = self.states['orientation']
        # self.orientation_error.update(np.matrix([0]))
        # self.orientation_error.update(np.matrix([0]))
        # self.orientation_error.update(np.matrix([0]))
        # self.orientation_error.update(np.matrix([0]))

    def update(self, Z, dt):
        # Z contains data for ['accel','odometer','gyro','mag_x', 'mag_y']
        #                       0       1          2      3        4

        # calibrate sensors
        Z = self.calibrate_sensors(Z)


        sensor_accel = Z[0]
        sensor_odometer = Z[1]
        sensor_gyro = Z[2]
        sensor_mag_x = Z[3]
        sensor_mag_y = Z[4]

        self.orientation_error.update_dt(dt)
        self.velocity_error.update_dt(dt)


        # integrate gyro to get orientation estimate
        self.gyro_integrated.add(sensor_gyro,dt)

        # calculate orientation from magnetometer
        mag = np.arctan2(sensor_mag_y,sensor_mag_x)
        
        # first orientation from magnetometer should be zero
        if self.mag_offset is None:
            self.mag_offset = mag
        mag -= self.mag_offset

        # fix orientation 2pi jumps
        mag_diff = mag - self.states['orientation']
        mag_diff -= np.round(mag_diff / (2*math.pi)) * (2*math.pi)
        mag = self.states['orientation'] + mag_diff
        self.mag = mag

        # update orientation error
        o_error = self.gyro_integrated.sum - mag
        self.orientation_error.last = o_error
        self.orientation_error.update(np.matrix([o_error]))
        self.orientation_error.predict()

        # output corrected orientation estimate
        self.states['orientation'] = self.gyro_integrated.sum - self.orientation_error.x[0,0]

        # integrate acceleration to get speed estimate
        self.accel_integrated.add(sensor_accel,dt)
        
        # update speed error
        vel_error = self.accel_integrated.sum - sensor_odometer
        self.velocity_error.update(np.matrix([vel_error]))
        self.velocity_error.predict()

        # output corrected speed estimate
        self.states['speed'] = self.accel_integrated.sum - self.velocity_error.x[0,0]

        # resolution of velocity vector
        velocity = Utils.rotate_points([(self.states['speed'],0)],self.states['orientation']/Utils.d2r)[0]

        # integrate velocity vector
        self.vx_integrated.add(velocity[0],dt)
        self.vy_integrated.add(velocity[1],dt)

        # feed through gyro
        self.states['yaw_rate'] = sensor_gyro
        # print self.states['yaw_rate'] / Utils.d2r

        # output positions
        self.states['pos_x'] = self.vx_integrated.sum
        self.states['pos_y'] = self.vy_integrated.sum

    def get_state(self, name):
        # name can be one of ['speed', 'orientation', 'yaw_rate', 'pos_x', 'pos_y']
        return self.states[name]

# import pandas as pd
# 
# def applyINS(Zs,dt=0.01):
#     """Feeds measurement data in Zs into INS and returns pandas DataFrame with states"""
#     ins = INS(dt)
#     n = Zs.shape[0]
#     states = dict()
#     for state in ins.states:
#         states[state] = np.empty(shape=(n))
#     for i in range(n):
#         ins.update(Zs[i,:],dt)
#         for state in ins.states:
#             states[state][i] = ins.states[state]

#     df = pd.DataFrame(states, np.arange(n)*dt)
#     return df
