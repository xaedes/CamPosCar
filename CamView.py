#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool


import pygame
import cv2

from cv2 import cv

from Draw import Draw
from Utils import Utils

from math import cos, sin

class CamView(object):
    """docstring for ClassName"""
    def __init__(self, car, imageArr,width = 150,height = 150, offset=(0,75), angle_offset = -25):
        super(CamView, self).__init__()
        self.car = car
        self.img = imageArr.transpose(1, 0, 2) # flip x and y axes
        self.width = width
        self.height = height
        self.view = None

        # offset specifies (in car coordinate system, y=driving direction), 
        # where the center of the view is
        self.offset = offset 

        # this angle is constantly added to self.car.theta
        self.angle_offset = angle_offset

        self.xy = self.car.x,self.car.y
        self.mousedown = False

    def update(self):
        pass

    def draw(self, screen):
        pos = Utils.translate_points(
                Utils.rotate_points(
                    [self.offset], 
                    self.angle_offset + self.car.theta - 90),
                self.car.x, self.car.y)[0]

        theta = self.angle_offset + self.car.theta - 90

        theta += 180 # upside down

        view = self.subimage(self.img, pos, theta , self.width, self.height)
        self.view = view
        # cv2.imshow("car " + str(self.car.id),view)
        # cv2.waitKey(1)

        Draw.draw_rotated_rect(screen,pos[0],pos[1],self.width,self.height,theta,Draw.RED)
            

    def register_events(self,events):
        events.register_callback("mousebuttondown", self.on_mousebuttondown)
        events.register_callback("mousebuttonup", self.on_mousebuttonup)
        events.register_callback("mousemotion", self.on_mousemotion)

    def on_mousebuttondown(self, event):
        if event.button == 1: # left 
            self.mousedown = True
        
    def on_mousebuttonup(self, event):
        if event.button == 1: # left 
            self.mousedown = False
        
    def on_mousemotion(self, event):
        if self.mousedown: 
            self.xy = event.pos
            

    def subimage(self, image, center, theta, width, height):
        # see rotatedrect.png

        theta *= Utils.d2r # convert to rad

        v_x = (cos(theta), sin(theta))
        v_y = (-sin(theta), cos(theta))
        s_x = center[0] - v_x[0] * (width / 2) - v_y[0] * (height / 2)
        s_y = center[1] - v_x[1] * (width / 2) - v_y[1] * (height / 2)

        mapping = np.array([[v_x[0],v_y[0], s_x],
                            [v_x[1],v_y[1], s_y]])

        return cv2.warpAffine(image,mapping,(width, height),flags=cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)

    def transform_camview_to_car_xy(self, points, flip_x = True, flip_y = False, flip_xy = False):
        transformed = points.copy()
        if flip_xy:
            transformed[:,0] = points[:,1]
            transformed[:,1] = points[:,0]
        if flip_x:
            transformed[:,0] = self.width - transformed[:,0]
        if flip_y:
            transformed[:,1] = self.height - transformed[:,1]
        transformed[:,0] -= self.offset[0]
        transformed[:,1] -= self.offset[1]
        return transformed

    def transform_car_xy_to_global(self, points, angle, global_x, global_y):
        transformed = np.array(Utils.rotate_points(points,angle))
        transformed += (global_x,global_y)
        return transformed
