#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np

import math


class Utils(object):
    d2r = math.pi / 180

    @classmethod
    def inRect(CLS, rect, i, j):
        x,y,w,h = rect
        return i >= x and i <= x + w - 1 and  j >= y and j <= y + h - 1

    @classmethod
    def distance_between(CLS, a, b):
        return math.sqrt(np.sum(np.square(np.array(a)-np.array(b))))

    @classmethod
    def rotate_points(CLS,points,angle,at=(0,0)):
        # angle in degree
        ax, ay = at
        cs,sn=math.cos(angle*Utils.d2r),math.sin(angle*Utils.d2r)
        if type(points) == np.ndarray:
            rotated = points.copy()
            rotated[:,0] = ax+(points[:,0]-ax) * cs - (points[:,1]-ay) * sn
            rotated[:,1] = ay+(points[:,0]-ax) * sn + (points[:,1]-ay) * cs
            return rotated
        else:
            return [(ax+(i-ax) * cs - (j-ay) * sn,ay+(i-ax) * sn + (j-ay) * cs) for (i,j) in points]

    
    @classmethod
    def translate_points(CLS,points,x,y):
        return [(i+x,j+y) for (i,j) in points]

    @classmethod
    def tangents(CLS,xs,ys):
        if len(xs) == 0:
            return np.array([])
        left_shifted_xs  = np.hstack([xs[-1],xs[:-1]]) 
        left_shifted_ys  = np.hstack([ys[-1],ys[:-1]]) 
        right_shifted_xs = np.hstack([xs[1:],xs[0]])
        right_shifted_ys = np.hstack([ys[1:],ys[0]])
        dx = left_shifted_xs - right_shifted_xs
        dy = left_shifted_ys - right_shifted_ys
        tangents = np.arctan2(dy,dx)/Utils.d2r
        diffs = np.hstack([0,np.diff(tangents)])
        diffs -= np.round(diffs/180)*180
        tangents = tangents[0] + diffs.cumsum()
        return tangents
        
    @classmethod
    def rotated_rect_points(CLS,center,angle,width,height):
        # angle in degree
        xs=[-width/2,
           width/2,
           width/2,
           -width/2]

        ys=[-height/2,
           -height/2,
           height/2,
           height/2]

        rotated = Utils.rotate_points(zip(xs,ys), angle)
        translated = Utils.translate_points(rotated,*center)

        return translated

    @classmethod
    def add_noise(CLS, value, variance):
        return value + (np.random.normal(0,math.sqrt(variance)) if variance > 0 else 0)

    @classmethod
    def zero_points(CLS, bw):
        yy,xx = np.meshgrid(*map(np.arange,reversed(bw.shape)))
        xx,yy = xx[bw == 0], yy[bw == 0] # select black pixel positions
        return np.array(zip(xx,yy))

    @classmethod
    def principal_axis_of_points(CLS, points):
        cov = np.cov(points.T)
        eig_vals, eig_vecs = np.linalg.eig(cov)

        # reversed sort, '-' causes the reverse
        eig_vecs_dsc = map(lambda tpl:tpl[1], sorted(zip(eig_vals, eig_vecs),key=(lambda tpl:-tpl[0])))

        return eig_vecs_dsc[0]:

        # return (1,1) # stub! todo: use image moments to calc principal axis    

    @classmethod
    def orientation_of_points(CLS, points):
        axis = CLS.principal_axis_of_points(points)
        return math.atan2(axis[1],axis[0]) # in rad