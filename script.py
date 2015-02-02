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
from Heuristic import Heuristic
from Car import Car
from Grid import Grid
from Draw import Draw
from Window import Window
from Events import Events
from Utils import Utils
from CamView import CamView
from INS import INS
from IMU import IMU
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
        # for k in range(1):
            # self.cars.append(Car(x=150+k*5,y=100,theta=np.random.randint(0,360),speed=np.random.randint(45,180)))
        self.cars.append(Car(x=50,y=250,theta=90,speed=0.3 * 1.5*90))
        self.cars.append(Car(x=50,y=250,theta=90,speed=1*90)) # [1] human
        self.cars.append(Car(x=50,y=250,theta=90,speed=1*90)) # [2] ghost of ins estimating [0]

        self.action = None
        self.human = HumanController()
        self.heuristic = Heuristic(self.lane)
        Node.heuristic = self.heuristic

        self.onestep = OneStepLookaheadController(self.cars,self.lane,self.heuristic)
        self.nstep = NStepLookaheadController(self.cars,self.lane, self.heuristic, 2)
        self.bestfirst = BestFirstController(self.cars,self.lane, self.heuristic)
        self.controller = self.bestfirst


        self.cars[0].camview = CamView(self.cars[0],self.background.arr)
        self.cars[0].camview.register_events(self.events)

        self.cars[0].controller = self.controller
        self.cars[0].collision = False
        self.cars[0].imu = IMU(self.cars[0])
        self.cars[0].ins = INS(self.cars[0].imu.calibration_noise)
        self.cars[0].ins.update_pose(self.cars[0].x, self.cars[0].y, self.cars[0].theta / Utils.d2r, gain = 1)
        self.insghost = INSGhostController(self.cars[0].ins)
        self.cars[1].controller = self.human
        self.cars[2].controller = self.insghost
        self.cars[2].collision = False
        self.cars[2].size *= 1.25
        self.cars[2].camview = CamView(self.cars[2],self.background.arr_dist_rgb,
                                        width = 275,height = 275, offset=(0,75), angle_offset = -25)
        self.cars[2].camview.register_events(self.events)

        self.cars[0].name = "actual"
        self.cars[1].name = "human"
        self.cars[2].name = "estimate"

        # this causes the controller of cars[0] to use the information from cars[0].ghost but act on cars[0]
        # self.cars[0].ghost = self.cars[2]

        # self.window = Window(self.screen, self.events, 300, 200, "caption")

        self.grid = Grid(50,50,*self.size)
        self.last_distance_grid_update = time() - 10
        self.update_distance_grid()

        self.done = False

        for car in self.cars:
            # save original speed
            if not hasattr(car,"speed_on"):
                car.speed_on = car.speed
            # toggle speed
            car.speed = car.speed_on - car.speed

            car.pause = not car.pause        

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

        # self.grid.draw(self.screen)

        self.lane.draw(self.screen)

        # self.camview.draw(self.screen)

        # blende tatsächlichen view in view von ins estimated ein
        actual_view = self.cars[0].camview.view
        ins_view = self.cars[2].camview.view
        if actual_view is not None and ins_view is not None:
            actual_view = actual_view.copy()
            ins_view = ins_view.copy()

            # horizontal center alignment of  actual view and ins view
            low_x = math.floor(actual_view.shape[0] / 2)
            hgh_x = low_x + math.ceil((actual_view.shape[0] / 2) - low_x)
            x1 = self.cars[2].camview.offset[0]+math.floor(ins_view.shape[0]/2)-low_x
            x2 = self.cars[2].camview.offset[0]+math.floor(ins_view.shape[0]/2)+hgh_x

            # vertical placement
            y1 = math.floor(self.cars[2].camview.offset[1])
            y2 = math.floor(self.cars[2].camview.offset[1])+actual_view.shape[1]

            # draw edges of actual_view with white in ins_view
            np.maximum(                  # only draw if brighter
                255-actual_view[:,:,:],  #
                ins_view[y1:y2,x1:x2,:], # 
                ins_view[y1:y2,x1:x2,:]) # dst, in-place
            
            # draw edges of actual_view with black in ins_view
            # np.minimum(                  # only draw if darker
            #     actual_view[:,:,:],
            #     ins_view[y1:y2,x1:x2,:],
            #     ins_view[y1:y2,x1:x2,:]) # dst, in-place
            
            # show image
            cv2.imshow("0 in 2",ins_view)

        #     # # bw
            bw = actual_view[:,:,0]

            # extract edge pixel positions from actual_view
            xx,yy = np.meshgrid(*map(np.arange,bw.shape))
            xx,yy = xx[bw == 0], yy[bw == 0] # select black pixel positions
            # edge = np.array(zip(yy,xx),dtype="int32")
            
            xx,yy = xx[::5],yy[::5]
            xx,yy = yy,xx
            if xx.shape[0] > 0:
                # transform edge positions into car coordinate system, with car position on (0,0) and y-axis pointing to driving direction
                # reverses camview offset and angle offset
                # yy -= self.cars[0].camview.offset[0]
                xx = self.cars[0].camview.width - (xx)
                xx -= self.cars[0].camview.offset[0] 
                yy -= self.cars[0].camview.offset[1] 
                # a second rotation to account for the car theta can be integrated into the camview.angle_offset rotation
                xxyy = np.array(Utils.rotate_points(zip(xx,yy),self.cars[0].camview.angle_offset + self.cars[2].theta))
                xx = xxyy[:,0]
                yy = xxyy[:,1]
                # add car offset
                xx += self.cars[2].x
                yy += self.cars[2].y

                # to use as index
                xx = np.round(xx).astype("int32")
                yy = np.round(yy).astype("int32")

            # transform edge positions into global card using ins estimate

            # show edge on distance transformation of bg
            tmp = (self.background.arr_dist/self.background.arr_dist.max()).copy()
            in_bounds = np.logical_and(np.logical_and(xx>=0,yy>=0),np.logical_and(xx<tmp.shape[0],yy<tmp.shape[1]))
            tmp[xx[in_bounds],yy[in_bounds]] = tmp.max()
            cv2.imshow("tmp",tmp)

        # # show distance transformation of bg
        # cv2.imshow("bg dist",self.background.arr_dist/self.background.arr_dist.max())

        # Draw car
        for car in self.cars:
            if self.controller is not None:
                if hasattr(self.controller,"action"):
                    car.draw(self.screen, self.controller.action)
                self.controller.draw(self.screen, car)

            else:
                car.draw(self.screen)
            if hasattr(car, "camview"):
                car.camview.draw(self.screen)

    def on_keyup(self, event):
        if event.key == pygame.K_SPACE:
            for car in self.cars:
                # save original speed
                if not hasattr(car,"speed_on"):
                    car.speed_on = car.speed
                # toggle speed
                car.speed = car.speed_on - car.speed

                car.pause = not car.pause

        elif self.lane.selected is not None \
           and event.key == pygame.K_DELETE:
            self.lane.remove_support_point(self.lane.selected)
            self.lane.selected = None
            self.update_distance_grid()

        elif event.key == pygame.K_RETURN:
            self.controller = self.human if self.controller != self.human else self.onestep

    def input(self):
        # get mouse info
        cursor = pygame.mouse.get_pos()
        (left_button, middle_button, right_button) = pygame.mouse.get_pressed() 
        

        # keys = pygame.key.get_pressed()
        # if self.lane.selected is not None:
        #     if keys[pygame.K_DELETE]:
        #         self.lane.remove_support_point(self.lane.selected)
        #         self.lane.selected = None
        #         self.update_distance_grid()

 
        # if keys[pygame.K_SPACE]:
        #     for car in self.cars:
        #         # save original speed
        #         if not hasattr(car,"speed_on"):
        #             car.speed_on = car.speed
        #         # toggle speed
        #         car.speed = car.speed_on - car.speed

        #         car.pause = True
        
        # if keys[pygame.K_RETURN]:
        #     self.controller = self.human if self.controller != self.human else self.onestep

    def update_distance_grid(self):
        # return
        if time() - self.last_distance_grid_update > 1 / 5:
            self.last_distance_grid_update = time()        
            for i in range(self.grid.width):
                for j in range(self.grid.height):
                    x,y = self.grid.xs[i], self.grid.ys[j]

                    closest_idx = self.lane.closest_sampled_idx(x, y)
                    distance = Utils.distance_between(
                        (self.lane.sampled_x[closest_idx],self.lane.sampled_y[closest_idx]),
                        (x,y))
                    # diff = np.array([self.lane.sampled_x[closest_idx]-x,self.lane.sampled_y[closest_idx]-y])
                    # distance = math.sqrt(np.sum(np.square(diff)))

                    self.grid.data[i,j] = distance*distance
            
    
    def register_events(self):
        self.events.register_callback("quit", self.on_quit)
        self.events.register_callback("laneupdate", self.on_laneupdate)
        self.events.register_callback("keyup", self.on_keyup)

    def on_quit(self, args):
        self.done = True

    def on_laneupdate(self, lane):
        if lane == self.lane:
            if self.lane.selected is None:
                self.update_distance_grid()
        # pass




    def update_ins(self,car,dt):
        # print "--"
        # print car.speed
        # print car.theta
        # print car.gyro

        # car.ins.update_pose(car.x, car.y, (car.theta) * Utils.d2r,gain=0.05)

        actual_view = self.cars[0].camview.view

        # bw
        bw = actual_view[:,:,0]


        # (x_corr, y_corr, theta_corr), error = self.optimize_correction(
        (x_corr, y_corr, theta_corr), error = self.optimize.optimize_correction(
            edge_points = Utils.zero_points(bw), 
            distances = self.background.arr_dist, 
            camview = self.cars[0].camview,
            x0 = car.ins.get_state("pos_x"),
            y0 = car.ins.get_state("pos_y"),
            theta0 = car.ins.get_state("orientation") / Utils.d2r,
            skip = 5,
            maxiter = 5,
            k = 1
            )


        print x_corr, y_corr, theta_corr, error

        car.ins.update_pose(
            x_corr, 
            y_corr, 
            theta_corr*Utils.d2r,
            # gain = 1)
            gain = 0.5*1/error if error != 0 else 1)

        car.ins.update(car.imu.get_sensor_array(), dt)

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

                    # update ins 
                    if hasattr(car,"ins"):
                        self.update_ins(car,dt)


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

