#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool


import pygame
import cv2

from cv2 import cv



class CamView(object):
    """docstring for ClassName"""
    def __init__(self, car, imageArr,width = 200,height = 200):
        super(CamView, self).__init__()
        self.car = car
        self.img = imageArr
        self.width = width
        self.height = height

        self.xy = self.car.x,self.car.y
        self.mousedown = False

    def update(self):
        pass

    def draw(self, screen):
        # pos = (self.height-self.car.y, self.width-self.car.x)
        pos = (self.xy[0],self.xy[1])
        print pos
        theta = 0
        # theta = self.car.theta
        view = self.subimage(self.img, pos, 1*(3.14/2)+theta * 3.14 / 180, self.width, self.height)
        cv2.imshow("",view)
        cv2.waitKey(1)
        # surf = pygame.surfarray.make_surface(view)

        # screen.blit(surf,(0,0))
        # pass

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
            

    def subimage(self,image, centre, theta, width, height):
        # http://stackoverflow.com/a/11627903/798588
       # output_image = cv.CreateImage((width, height), image.depth, image.nChannels)
       mapping = np.array([[np.cos(theta), -np.sin(theta), centre[0]],
                           [np.sin(theta), np.cos(theta), centre[1]]])
       # map_matrix_cv = cv.fromarray(mapping)
       # cv.GetQuadrangleSubPix(image, output_image, map_matrix_cv)
       return cv2.warpAffine(image,mapping,(width, height),borderMode=cv2.BORDER_REPLICATE)
       # return output_image    