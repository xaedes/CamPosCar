#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import math                        # Mathefunktionen braucht man auch häufiger mal

import pandas as pd       # pip install pandas
import rosbag_pandas      # pip install rosbag_pandas
import ottocar_common.RosbagToPandas as rb2p
import ottocar_common.Utils as Utils

import os

class ImuCalibration(object):
    """docstring for ImuCalibration"""
    def __init__(self, mag_calib_bag_fn=None, refresh_cache=False):
        super(ImuCalibration, self).__init__()

        # magnetometer calibration
        if mag_calib_bag_fn is None:
            mag_calib_bag_fn = os.path.dirname(os.path.abspath(__file__))  + "/../../calibration_data/mag/0.bag"
            # mag_calib_bag_fn = os.path.dirname(os.path.abspath(__file__))  + "/../../calibration_data/mag_sparkfun_hard_and_soft.bag"
        # mag_calib_bag_fn = os.path.dirname(os.path.abspath(__file__))  + "/../../calibration_data/mag.bag"

        # sensor variances
        in_rest_position_bag_fn = os.path.dirname(os.path.abspath(__file__))  + "/../../calibration_data/in_rest_position.bag"
        gyro_scale_pkl_fn = os.path.dirname(os.path.abspath(__file__))  + "/../../calibration_data/gyro_scale/cw/0.bag.pkl"

        cache_suffix = ".pkl"

        df_mag = None
        if os.path.isfile(mag_calib_bag_fn + cache_suffix) and not refresh_cache:
            try:
                df_mag = pd.read_pickle(mag_calib_bag_fn + cache_suffix)
            except:
                df_mag = None
        if df_mag is None:
            df_mag = rosbag_pandas.bag_to_dataframe(mag_calib_bag_fn)
            df_mag = rb2p.reindex_dataframe(df_mag,df_mag.sensors_imu_data_raw__angular_velocity_x)
            df_mag.to_pickle(mag_calib_bag_fn + cache_suffix)

        self.mag_offset, self.mag_scale = self.calc_mag_calib(df_mag)

        df_rest = None
        if os.path.isfile(in_rest_position_bag_fn + cache_suffix) and not refresh_cache:
            try:
                df_rest = pd.read_pickle(in_rest_position_bag_fn + cache_suffix)
            except:
                df_rest = None
        if df_rest is None:
            df_rest = rosbag_pandas.bag_to_dataframe(in_rest_position_bag_fn)
            df_rest = rb2p.reindex_dataframe(df_rest,df_rest.sensors_imu_data_raw__angular_velocity_x)
            df_rest.to_pickle(in_rest_position_bag_fn + cache_suffix,)

        df_rest.sensors_imu_data_raw__magnetometer_x -= self.mag_offset[0]
        df_rest.sensors_imu_data_raw__magnetometer_y -= self.mag_offset[1]
        df_rest.sensors_imu_data_raw__magnetometer_x /= self.mag_scale[0]
        df_rest.sensors_imu_data_raw__magnetometer_y /= self.mag_scale[1]
        
        self.gyro_z_bias = df_rest.sensors_imu_data_raw__angular_velocity_z.mean()
        self.gyro_z_std = df_rest.sensors_imu_data_raw__angular_velocity_z.std()
        self.gyro_z_variance = self.gyro_z_std ** 2

        self.accel_x_bias = df_rest.sensors_imu_data_raw__linear_acceleration_x.mean()
        self.accel_x_std = df_rest.sensors_imu_data_raw__linear_acceleration_x.std()
        self.accel_x_variance = self.accel_x_std ** 2
        
        mag_theta = np.arctan2(
            df_rest.sensors_imu_data_raw__magnetometer_y,
            df_rest.sensors_imu_data_raw__magnetometer_x)

        self.mag_theta_std = mag_theta.std()
        self.mag_theta_variance = self.mag_theta_std ** 2

        # self.mag_theta_variance = 10*50 * 3.14 / 180
        
        self.odometer_std = 0.00480059018124
        self.odometer_variance = self.odometer_std ** 2

        ax = df_rest.sensors_imu_data_raw__linear_acceleration_x
        ay = df_rest.sensors_imu_data_raw__linear_acceleration_y
        az = df_rest.sensors_imu_data_raw__linear_acceleration_z
        g = np.sqrt(ax**2+ay**2+az**2)
        self.accel_scale = 9.81 /  g.mean()

        df_gyro_scale = pd.read_pickle(gyro_scale_pkl_fn)
        # idx=np.arange(df.index.shape[0])
        gyro_scales = ImuCalibration.calc_gyro_scales_df(df_gyro_scale)

        self.gyro_scale = gyro_scales.mean()

        # # mit allan varianz über 12h daten bestimmt:
        # gyro_std = 0.863*1e-4
        # accel_std = 2.784*1e-2
        
    def calc_mag_calib(self, df):
        mag = np.vstack([df.sensors_imu_data_raw__magnetometer_x, df.sensors_imu_data_raw__magnetometer_y]).T
        # remove outliers
        mag_std = np.std(mag,axis=0)
        mag_median = np.median(mag,axis=0)
        sel = np.logical_and(
            np.abs(mag[:,0]-mag_median[0]) < 3*mag_std[0],
            np.abs(mag[:,1]-mag_median[1]) < 3*mag_std[1])
        mag = mag[sel,:]

        # calculate calibration
        mag_min = np.min(mag,axis=0)
        mag_max = np.max(mag,axis=0)
        offset = (mag_min+mag_max)/2.
        scale = (mag_max-mag_min)/2.
        return offset, scale

    @classmethod
    def peak_indices(CLS,data,peak_threshold=0.8):
        '''Returns single indices into data of data peaks'''
        # select data peaks
        d_min = data.min()
        d_max = data.max()
        normalized_data = (data-(d_max+d_min)/2)/((d_max-d_min)/2)
        sel=normalized_data>peak_threshold
        
        # indices of data peaks
        indices = np.arange(data.shape[0])[sel]
        #return indices
        
        # create index clusters by splitting on large jumps
        index_diffs = Utils.diffKeepLength(indices)
        threshold = (np.min(index_diffs)+np.max(index_diffs))/2
        indices_indices = np.arange(indices.shape[0])
        clustered_indices = np.split(indices,indices_indices[index_diffs>threshold])
        peaks=np.array(map(lambda index_cluster: np.round(index_cluster.mean()).astype('int'),clustered_indices))
        return peaks

    @classmethod
    def calc_gyro_scale(CLS,dts,gyro_z,interval):
        gyro_integrated = (gyro_z*dts)[interval].sum()
        gyro_scale = (2*math.pi)/abs(gyro_integrated)
        return gyro_scale
    
    @classmethod
    def calc_gyro_scales(CLS,peaked_series, gyro_series,peak_threshold=0.8):
        # gyro in rad/s
        indices = np.arange(peaked_series.values.shape[0])
        timestamps = np.array(peaked_series.index)
        peaks = CLS.peak_indices(peaked_series.values,peak_threshold)
        intervals=np.split(indices,peaks)[1:-1]
        dts = Utils.diffKeepLength(timestamps)
        
        # print map(len,intervals)
        gyro_scales = np.array(map(
            lambda interval:CLS.calc_gyro_scale(dts,gyro_series.values,interval),
            intervals))
        
        return gyro_scales

    @classmethod
    def calc_gyro_scales_df(CLS,df,peak_threshold=0.8):
        return CLS.calc_gyro_scales(
            df.sensors_imu_data_raw__magnetometer_x, 
            df.sensors_imu_data_raw__angular_velocity_z,
            peak_threshold)

