#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool


import pygame

"""
 Show how to use a sprite backed by a graphic.
 
 Sample Python/Pygame Programs
 Simpson College Computer Science
 http://programarcadegames.com/
 http://simpson.edu/computer-science/
 
 Explanation video: http://youtu.be/vRB_983kUMc
"""
 
import pygame

import cv2
from cv2 import cv

from time import time

from Background import Background
from Lane import Lane
from Controllers import *
from Car import Car
from Draw import Draw
from Window import Window
from Events import Events
from Utils import Utils
from CamView import CamView
# from INS import INS
# from IMU import IMU
from Optimize import Optimize


import math
from copy import copy
# Define some colors

d2r = math.pi / 180


class App(object):
    """docstring for App"""
    def __init__(self):
        super(App, self).__init__()
        # load background
        self.background = Background(filename="background.png")

        # get array copy of background image
        self.background.arr = pygame.surfarray.array3d(self.background.img)

        # create bw from image
        _,self.background.arr_bw = cv2.threshold(self.background.arr[:,:,0],128,1,cv2.THRESH_BINARY)
        
        # print self.background.arr_bw.shape, self.background.arr_bw.dtype
        # self.background.arr_dist = cv2.distanceTransform(self.background.arr_bw, cv.CV_DIST_L1, 3)
        
        # get nearest (zero) pixel labels with corresponding distances
        self.background.arr_dist,self.labels = cv2.distanceTransformWithLabels(self.background.arr_bw, cv.CV_DIST_L1, 3,labelType = cv2.DIST_LABEL_PIXEL)

        ### get x,y coordinates for each label
        # get positions of zero points
        zero_points = Utils.zero_points(self.background.arr_bw)
        # get labels for zero points
        zero_labels = self.labels[zero_points[:,0],zero_points[:,1]]
        # create dictionary mapping labels to zero point positions
        self.label_positions = dict(zip(zero_labels,zip(zero_points[:,0],zero_points[:,1])))


        # provide a rgb variant of dist for display
        self.background.arr_dist_rgb = self.background.arr.copy()
        self.background.arr_dist_rgb[:,:,0] = self.background.arr_dist
        self.background.arr_dist_rgb[:,:,1] = self.background.arr_dist
        self.background.arr_dist_rgb[:,:,2] = self.background.arr_dist
        # print a.shape

        self.setup_pygame()
        self.background.arr_dist = cv2.distanceTransform(self.background.arr_bw, cv.CV_DIST_L1, 3)

        self.events = Events()



        self.lane = Lane(self.events)
        self.lane.load("parkour.sv")
        # self.lane.add_support_point(100,100)
        # self.lane.add_support_point(200,100)
        # self.lane.add_support_point(200,200)
        # self.lane.add_support_point(100,200)

        self.optimize = Optimize(self.lane)

        self.cars = []
        self.cars.append(Car(x=100,y=100,theta=-45,speed=0)) # representation for actual car
        self.cars.append(Car(x=100,y=100,theta=-45,speed=0)) # representation for ins estimate
        self.cars.append(Car(x=100,y=100,theta=-45,speed=0)) # representation for ins estimate optimization single pass
        self.cars.append(Car(x=100,y=100,theta=-45,speed=0)) # representation for ins estimate optimization multi pass

        for car in self.cars:
            car.color = Draw.WHITE
        self.cars[2].color = Draw.YELLOW
        self.cars[3].color = Draw.RED

        self.action = None

        self.dragdrop = DragAndDropController(self.events)
        self.controller = self.dragdrop


        # self.cars[0].camview = CamView(self.cars[0],self.background.arr)
        # self.cars[0].camview.register_events(self.events)

        self.cars[0].name = "actual"
        self.cars[1].name = "estimate"
        self.cars[2].name = "opt"
        self.cars[3].name = "opt*"
        self.cars[0].controller = self.controller
        self.cars[1].controller = self.controller
        self.cars[0].camview = CamView(self.cars[0],self.background.arr)

        self.cars[2].controller = OptimizeNearestEdgeXYSinglePass(
            optimize = self.optimize, 
            labels = self.labels, 
            label_positions = self.label_positions, 
            camview = self.cars[0].camview, 
            estimate_car = self.cars[1])
        self.cars[3].controller = OptimizeNearestEdgeXYMultiPass(
            optimize = self.optimize, 
            labels = self.labels, 
            label_positions = self.label_positions, 
            camview = self.cars[0].camview, 
            estimate_car = self.cars[1])

        # self.window = Window(self.screen, self.events, 300, 200, "caption")

        self.done = False

        self.cursor = (0,0)

        self.register_events()
        self.spin()

    def setup_pygame(self):
        pygame.init()
         
        # Set the width and height of the screen [width, height]
        self.size = (self.background.rect.width, self.background.rect.height)
        self.screen = pygame.display.set_mode(self.size)

        self.font = pygame.font.SysFont("arial",10)
        Draw.font = self.font         

        pygame.display.set_caption("My Game")

    def draw_string(self,string,x,y,color=Draw.BLACK):
        Draw.draw_string(self.screen,self.font,string,x,y,color)


    def draw(self):
        self.background.draw(self.screen)
        # Draw.draw_nparr(self.screen, self.background.arr_dist_rgb)
        
        camview = self.cars[0].camview
        actual_view = camview.view

        if actual_view is not None:

            # bw
            bw = actual_view[:,:,0]

            skip = 5
            edge_points = Utils.zero_points(bw)[::skip,:]

            transformed = camview.transform_camview_to_car_xy(edge_points,
                flip_x = True, flip_y = False, flip_xy = False
                )
            
            transformed = camview.transform_car_xy_to_global(transformed,
                    angle = self.cars[1].theta + camview.angle_offset,
                    global_x = self.cars[1].x, 
                    global_y = self.cars[1].y)

            xx,yy = transformed[:,0], transformed[:,1]

            ## show edge on distance transformation of bg
            # get arr_dist copy scaled to 0..1
            # tmp = (self.background.arr_dist/self.background.arr_dist.max()).copy()
            tmp = 1-(self.background.arr_bw/self.background.arr_bw.max()).copy()
            # select points that in bound of the drawing area
            in_bounds = np.logical_and(np.logical_and(xx>=0,yy>=0),np.logical_and(xx<tmp.shape[0],yy<tmp.shape[1]))
            # set points that are in bounds to maximum value, i.e. white
            tmp[xx[in_bounds],yy[in_bounds]] = tmp.max()

            # get nearest points on bg edge of all transformed points in bounds
            nearest_edge = np.array([self.label_positions[label] for label in self.labels[xx[in_bounds],yy[in_bounds]]])
            # set nearest points to white
            tmp[nearest_edge[:,0],nearest_edge[:,1]] = tmp.max()

            # show cv2 image in extra window
            # cv2.imshow("tmp",tmp)

            # blit what we draw so far
            Draw.draw_nparr(self.screen, 255*tmp)
            
            # draw lines from transformed points to corresponding nearest bg edge point
            for i in range(nearest_edge.shape[0]):
                pygame.draw.aaline(self.screen, Draw.GRAY, 
                    (xx[in_bounds][i],yy[in_bounds][i]),
                    (nearest_edge[i,0],nearest_edge[i,1]))

            # self.cars[2].x = self.cars[1].x + (nearest_edge[:,0] - xx[in_bounds]).mean()
            # self.cars[2].y = self.cars[1].y + (nearest_edge[:,1] - yy[in_bounds]).mean()
            # self.cars[2].theta = self.cars[1].theta

        self.lane.draw(self.screen)

        # draw cursor position
        pygame.draw.circle(self.screen, Draw.WHITE, (self.cursor[0], self.cursor[1]), 2, 1)
        label = self.labels[self.cursor[0],self.cursor[1]]
        x,y = self.label_positions[label]
        pygame.draw.circle(self.screen, Draw.WHITE, (int(x+0.5),int(y+0.5)), 2, 1)
        # print self.label_positions[label]

        # Draw car
        for car in self.cars:
            if self.controller is not None:
                if hasattr(self.controller,"action"):
                    car.draw(self.screen, self.controller.action)
                else:
                    car.draw(self.screen)
                self.controller.draw(self.screen, car)

            else:
                car.draw(self.screen)
            if hasattr(car, "camview"):
                car.camview.draw(self.screen)

    def on_keyup(self, event):
        if self.lane.selected is not None \
           and event.key == pygame.K_DELETE:
            self.lane.remove_support_point(self.lane.selected)
            self.lane.selected = None

        elif event.key == pygame.K_RETURN:
            self.controller = self.human if self.controller != self.human else self.onestep

    def on_mousemotion(self, event):
        self.cursor = event.pos

    def input(self):
        # get mouse info
        cursor = pygame.mouse.get_pos()
        (left_button, middle_button, right_button) = pygame.mouse.get_pressed() 
        
    def register_events(self):
        self.events.register_callback("quit", self.on_quit)
        self.events.register_callback("laneupdate", self.on_laneupdate)
        self.events.register_callback("keyup", self.on_keyup)
        self.events.register_callback("mousemotion", self.on_mousemotion)

    def on_quit(self, args):
        self.done = True

    def on_laneupdate(self, lane):
        pass



    def spin(self):
        # Loop until the user clicks the close button.
        self.done = False
         
        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        self.last_time = time()


        # -------- Main Program Loop -----------
        while not self.done:
            dt = time()-self.last_time
            self.last_time = time()
            # --- Main event loop

            for event in pygame.event.get(): # User did something
                if event.type in self.events.pygame_mappings:
                    self.events.fire_callbacks(self.events.pygame_mappings[event.type], event)

                # if event.type == pygame.QUIT: # If user clicked close
                    # done = True # Flag that we are done so we exit this loop
            self.input()

            # --- Game logic should go here

            # apply controllers
            for car in self.cars:
                if not car.pause:
                    # eventually set default controller
                    if car.controller is None and self.controller is not None:
                        car.controller = self.controller

                    # apply controller
                    if car.controller is not None:
                        car.controller.update(car,dt)


            # --- Drawing code should go here
         
            # First, clear the screen to white. Don't put other drawing commands
            # above this, or they will be erased with this command.
            self.screen.fill(Draw.WHITE)
         
            self.draw()
            
            
            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()
            

            # --- Limit to 60 frames per second
            clock.tick(60)
         
        # Close the window and quit.
        # If you forget this line, the program will 'hang'
        # on exit if running from IDLE.
        pygame.quit()


App()

