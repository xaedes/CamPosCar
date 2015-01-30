#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import math
from Draw import Draw
from Utils import Utils



import pygame

car_id = 0
class Car(object):

    """docstring for Car"""
    def __init__(self, x, y, theta, speed=2*90, max_steer=0.2*15/(1/60), size=10):
        super(Car, self).__init__()
        self.size = size
        self.collision = True
        self.x = x
        self.y = y
        self.theta = theta # in degree
        self.gyro = 0  # in degree / s
        self.speed = speed # px / s
        
        self.vx, self.vy = 0, 0
        self.ax, self.ay = 0, 0
        self.ax_local, self.ay_local = 0, 0
        self.last = {}

        global car_id
        self.id = car_id
        car_id += 1

        self.max_steer = max_steer # in degree/s
        self.actions = np.linspace(-1,1,11)

        self.controller = None
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

        # calculate gyro from action
        self.gyro = -action * self.max_steer


        # save last state
        self.last = {
            "x": self.x,
            "y": self.y,
            "theta": self.theta,
            "vx": self.vx,
            "vy": self.vy,
            "ax": self.ax,
            "ay": self.ay,
            "ax_local": self.ax_local,
            "ay_local": self.ay_local
        }

        # update orientation
        self.theta += self.gyro * dt  # in degree

        # if gyro is below threshold linear motion is assumed
        if abs(self.gyro) < 1e-3:
            self.vx = math.cos(self.theta*Utils.d2r) * self.speed * dt
            self.vy = math.sin(self.theta*Utils.d2r) * self.speed * dt

            # calculate global acceleration
            self.ax = (self.vx - self.last["vx"]) / dt
            self.ay = (self.vy - self.last["vy"]) / dt
            g = 0.4
            self.ax = g * self.ax + (1-g) * self.last["ax"]
            self.ay = g * self.ay + (1-g) * self.last["ay"]

            # calculate local acceleration
            self.ax_local, self.ay_local = Utils.rotate_points([(self.ax,self.ay)],-self.theta)[0]
            self.ax_local = g * self.ax_local + (1-g) * self.last["ax_local"]
            self.ay_local = g * self.ay_local + (1-g) * self.last["ay_local"]

        else:
            # otherwise apply uniform circular motion

            # see whiteboard in wiki
            # notes: whiteboard 'c' is 'b' here
            
            # orientation difference
            d_th = abs(self.theta - self.last["theta"]) * Utils.d2r
            
            # radius of circle on which's arc is moved
            r = self.speed * dt / d_th

            # tangent of movement
            # according to the whiteboard it should be the last tangent, but it only properly works with the new tangent
            # v = math.cos(last_theta*Utils.d2r) , math.sin(last_theta*Utils.d2r) # last tangent
            v = math.cos(self.theta*Utils.d2r) , math.sin(self.theta*Utils.d2r)  # new tangent
            # points from (x,y) towards the circle center, is normal of tangent v
            u = v[1],-v[0] 

            # projection of new position (x+vx,y+vy) onto u
            a = r * (1 - math.cos(d_th)) 
            # projection of new position (x+vx,y+vy) onto v  ; (b is named 'c' in the whiteboard)
            b = r * math.sin(d_th) 

            # velocity vector
            self.vx = u[0] * a + v[0] * b
            self.vy = u[1] * a + v[1] * b

            # http://dev.physicslab.org/Document.aspx?doctype=3&filename=CircularMotion_CentripetalAcceleration.xml
            # centripetal acceleration a_c in direction of the circle center (i.e. along u):
            a_c = 2 * math.pi * r * d_th

            # calculate global acceleration
            self.ax = a_c * u[0]
            self.ay = a_c * u[1]

            # calculate local acceleration
            self.ax_local = 0 
            self.ay_local = -a_c

        self.x += self.vx
        self.y += self.vy



        # if self.id == 0:
        #     print "---"
        #     print "self.ax", self.ax
        #     print "self.ay", self.ay
        #     print "self.ax_local", self.ax_local
        #     print "self.ay_local", self.ay_local
            # print self.gyro

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

