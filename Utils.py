#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np

import math

d2r = math.pi / 180

class Utils(object):

    @classmethod
    def inRect(CLS, rect, i, j):
        x,y,w,h = rect
        return i >= x and i <= x + w - 1 and  j >= y and j <= y + h - 1

    @classmethod
    def distance_between(CLS, a, b):
        return math.sqrt(np.sum(np.square(np.array(a)-np.array(b))))

    @classmethod
    def rotate_points(CLS,points,angle,at=(0,0)):
        ax, ay = at
        d2r=math.pi/180
        cs,sn=math.cos(angle*d2r),math.sin(angle*d2r)
        return [(ax+(i-ax) * cs - (j-ay) * sn,ay+(i-ax) * sn + (j-ay) * cs) for (i,j) in points]
    
    @classmethod
    def translate_points(CLS,points,x,y):
        return [(i+x,j+y) for (i,j) in points]

    @classmethod
    def tangents(CLS,xs,ys):
        left_shifted_xs  = np.hstack([xs[-1],xs[:-1]]) 
        left_shifted_y  = np.hstack([ys[-1],ys[:-1]]) 
        right_shifted_x = np.hstack([xs[1:],xs[-1]])
        right_shifted_y = np.hstack([ys[1:],ys[-1]])
        dx = left_shifted_x - right_shifted_x
        dy = left_shifted_y - right_shifted_y
        tangents = np.arctan2(dy,dx)/d2r
        # diffs = np.hstack([0,np.diff(tangents)])
        # diffs -= np.round(diffs/360)*360
        # tangents = tangents[0] + diffs.cumsum()
        return tangents
        