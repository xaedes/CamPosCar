#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool


import pygame
import cv2

from cv2 import cv

from Draw import Draw
from Utils import Utils

class CamView(object):
    """docstring for ClassName"""
    def __init__(self, car, imageArr,width = 200,height = 150):
        super(CamView, self).__init__()
        self.car = car
        self.img = imageArr.transpose(1, 0, 2) # flip x and y axes
        self.width = width
        self.height = height

        self.xy = self.car.x,self.car.y
        self.mousedown = False

    def update(self):
        pass

    def draw(self, screen):
        # pos = (self.height-self.car.y, self.width-self.car.x)
        pos = (self.car.x, self.car.y)
        # pos = (self.xy[0],self.xy[1])
        # print pos,
        # print self.img.shape,
        # print self.img.transpose(1, 0, 2).shape,
        # print ""
        # theta = 22.5
        theta = self.car.theta
        # cv2.imshow("foo?",self.img)
        view = self.subimage(self.img, pos, theta , self.width, self.height)
        cv2.imshow("",view)
        cv2.waitKey(1)
        # surf = pygame.surfarray.make_surface(view)

        # screen.blit(surf,(0,0))
        Draw.draw_rotated_rect(screen,pos[0],pos[1],self.width,self.height,theta,Draw.RED)
            
        # print Utils.rotated_rect_points(pos,theta,self.width,self.height)
        # pygame.draw.polygon(screen, Draw.RED, Utils.rotated_rect_points(pos,theta,self.width,self.height), 1)
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
            

    # def subimage(self,image, centre, theta, width, height):
    #     # http://stackoverflow.com/a/11627903/798588
    #     # output_image = cv.CreateImage((width, height), image.depth, image.nChannels)
    #     mapping = np.array([[np.cos(theta), -np.sin(theta), -centre[0]],
    #                        [np.sin(theta), np.cos(theta), -centre[1]]])
    #     print mapping
    #     # map_matrix_cv = cv.fromarray(mapping)
    #     # cv.GetQuadrangleSubPix(image, output_image, map_matrix_cv)
    #     return cv2.warpAffine(image,mapping,(width, height),borderMode=cv2.BORDER_REPLICATE)
    #     # return output_image    

    # theta in degree
    def subimage(self,image, center, theta, width, height):

        #http://answers.opencv.org/question/497/extract-a-rotatedrect-area/
        # thanks to http://felix.abecassis.me/2011/10/opencv-rotation-deskewing/
        if theta < -45.:
            theta += 90.0
            height, width = width, height
        

        # add white border to image
        padded = np.ones(shape=(image.shape[0]+1,image.shape[1]+1,3),dtype=image.dtype) * 255
        padded[1:padded.shape[0],1:padded.shape[1],:] = image[:,:,:]

        # crop to bounding bounding box of rotated rect
        rrPoints = np.array([Utils.rotated_rect_points(center,theta,width,height)],dtype="int32")
        boundingRect = cv2.boundingRect(rrPoints)
        x,y,w,h = boundingRect
        croppedCenter = (x+w/2+1,y+h/2+1)
        cropped = cv2.getRectSubPix(padded, (w, h), croppedCenter)

        cv2.imshow("cropped",cropped)

        # get the rotation matrix
        M = cv2.getRotationMatrix2D((w/2,h/2), theta , 1.0) 

        print ""

        croppedPoints = np.array([[0,0],[w,0],[0,h],[w,h]],dtype="float32")
        croppedPointsM = (croppedPoints - M[:,2]/2).dot(M[:,:2])+M[:,2]/2
        croppedPointsMBBox = cv2.boundingRect(np.array([croppedPointsM],dtype="float32"))
        dsize=croppedPointsMBBox[2:]
        # print croppedPointsM

        # M[:,2] += croppedPointsMBBox[:2]

        # perform the affine transformation
        warped = cv2.warpAffine(cropped,M,dsize,borderMode=cv2.BORDER_TRANSPARENT ,flags=cv2.INTER_NEAREST)

        return warped
        # crop the resulting image
        cropped = cv2.getRectSubPix(warped, (width, height), center)
        # croppes = warped[round(center-width/2)]

        return cropped

