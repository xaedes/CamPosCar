#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import math
from Draw import Draw
from Utils import Utils
d2r = math.pi / 180

import pygame

car_id = 0
class Car(object):

    """docstring for Car"""
    def __init__(self, x, y, theta, speed=2*90, max_steer=0.2*15/(1/60), size=10):
        super(Car, self).__init__()
        self.x = x
        self.y = y
        self.theta = theta # in degree
        self.size = size
        self.speed = speed # px / s
        self.actions = np.linspace(-1,1,3)
        self.max_steer = max_steer # in degree/s
        global car_id
        self.id = car_id
        self.controller = None
        car_id += 1
        self.pause = False

    def collision_radius(self):
        return self.size * 1.2

    def steers(self):
        return self.actions * self.max_steer

    def forward(self,action,dt):
        assert action in self.actions
    #     # action == -1  : left
    #     # action ==  0  : middle
    #     # action ==  1  : right
        # if dt > 0:
            # print 1/dt
            # print 1/dt
        steer = action * self.max_steer
        self.theta -= steer * dt 
        vx = math.cos(self.theta*d2r) * self.speed * dt
        vy = math.sin(self.theta*d2r) * self.speed * dt
        self.x += vx
        self.y += vy

        return self

    def draw(self,screen, action = None):
        color = Draw.BLACK
        # draw collision area
        pygame.draw.circle(screen, color, (int(self.x+0.5), int(self.y+0.5)), int(self.collision_radius()+0.5), 1)

        # draw car itself
        Draw.draw_rotated_rect(screen,self.x,self.y,self.size,self.size*0.8,self.theta,color)

        # draw action lines
        action_lines={}
        m = self.size * 1.10
        l = self.size * 0.5
        for a in self.actions:
            action_line = Utils.translate_points(Utils.rotate_points([(0,0),(m,-a*l)],self.theta),self.x,self.y)
            color = color
            width = 2 if action == a else 1
            pygame.draw.lines(screen,color,False,action_line,width)

