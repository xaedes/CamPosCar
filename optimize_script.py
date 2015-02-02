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
        
        self.background = Background(filename="background.png")
        self.background.arr = pygame.surfarray.array3d(self.background.img)
        _,self.background.arr_bw = cv2.threshold(self.background.arr[:,:,0],128,1,cv2.THRESH_BINARY)
        # print self.background.arr_bw.shape, self.background.arr_bw.dtype
        self.background.arr_dist = cv2.distanceTransform(self.background.arr_bw, cv.CV_DIST_L1, 3)
        self.background.arr_dist_rgb = self.background.arr.copy()
        self.background.arr_dist_rgb[:,:,0] = self.background.arr_dist
        self.background.arr_dist_rgb[:,:,1] = self.background.arr_dist
        self.background.arr_dist_rgb[:,:,2] = self.background.arr_dist
        # print a.shape

        self.setup_pygame()

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

        for car in self.cars:
            car.color = Draw.WHITE

        self.action = None

        self.dragdrop = DragAndDropController(self.events)
        self.controller = self.dragdrop


        # self.cars[0].camview = CamView(self.cars[0],self.background.arr)
        # self.cars[0].camview.register_events(self.events)

        self.cars[0].name = "actual"
        self.cars[1].name = "estimate"
        self.cars[0].controller = self.controller
        self.cars[1].controller = self.controller
        self.cars[0].camview = CamView(self.cars[0],self.background.arr)

        # self.window = Window(self.screen, self.events, 300, 200, "caption")

        self.done = False

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

            edge_points = self.optimize.zero_points(bw)

            transformed = camview.transform_camview_to_car_xy(edge_points,
                flip_x = True, flip_y = False, flip_xy = True
                )
            transformed = camview.transform_car_xy_to_global(transformed,
                    angle = self.cars[1].theta + camview.angle_offset,
                    global_x = self.cars[1].x, 
                    global_y = self.cars[1].y)

            xx,yy = transformed[:,0], transformed[:,1]

            # show edge on distance transformation of bg
            tmp = (self.background.arr_dist/self.background.arr_dist.max()).copy()
            in_bounds = np.logical_and(np.logical_and(xx>=0,yy>=0),np.logical_and(xx<tmp.shape[0],yy<tmp.shape[1]))
            tmp[xx[in_bounds],yy[in_bounds]] = tmp.max()

            # cv2.imshow("tmp",tmp)

            Draw.draw_nparr(self.screen, 255*tmp)

        self.lane.draw(self.screen)

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

    def input(self):
        # get mouse info
        cursor = pygame.mouse.get_pos()
        (left_button, middle_button, right_button) = pygame.mouse.get_pressed() 
        
    def register_events(self):
        self.events.register_callback("quit", self.on_quit)
        self.events.register_callback("laneupdate", self.on_laneupdate)
        self.events.register_callback("keyup", self.on_keyup)

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

