#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import math
d2r = math.pi / 180

class Car(object):
    """docstring for Car"""
    def __init__(self, x, y, theta, speed=10, max_steer=5/(1/60), size=10):
        super(Car, self).__init__()
        self.x = x
        self.y = y
        self.theta = theta # in degree
        self.size = size
        self.speed = speed # px / s
        self.actions = np.linspace(-1,1,7)
        self.max_steer = max_steer # in degree/s
    def steers(self):
        return self.actions * self.max_steer

    def forward(self,action,dt):
        assert action in self.actions
    #     # action == -1  : left
    #     # action ==  0  : middle
    #     # action ==  1  : right
    	if dt > 0:
    		print 1/dt
    		# print 1/dt
        steer = action * self.max_steer
        self.theta -= steer * dt 
        vx = math.cos(self.theta*d2r) * self.speed * dt
        vy = math.sin(self.theta*d2r) * self.speed * dt
        self.x += vx
        self.y += vy

        return self

