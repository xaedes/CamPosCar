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

import math
from copy import copy
# Define some colors

d2r = math.pi / 180


class App(object):
    """docstring for App"""
    def __init__(self):
        super(App, self).__init__()
        
        self.background = Background(filename="background.png")

        # a=pygame.surfarray.array3d(self.background.img)
        # print a.shape

        self.setup_pygame()

        self.events = Events()


        self.lane = Lane(self.events)
        self.lane.load("parkour.sv")
        # self.lane.add_support_point(100,100)
        # self.lane.add_support_point(200,100)
        # self.lane.add_support_point(200,200)
        # self.lane.add_support_point(100,200)

        self.cars = []
        # for k in range(1):
            # self.cars.append(Car(x=150+k*5,y=100,theta=np.random.randint(0,360),speed=np.random.randint(45,180)))
        self.cars.append(Car(x=250,y=100,theta=-45,speed=0.5*90))
        self.cars.append(Car(x=250,y=200,theta=-45,speed=1*90))
        self.action = None
        self.human = HumanController()

        self.camview = CamView(self.cars[0],pygame.surfarray.array3d(self.background.img))
        self.camview.register_events(self.events)

        self.cars[-1].controller = self.human
        self.heuristic = Heuristic(self.lane)
        Node.heuristic = self.heuristic
        self.onestep = OneStepLookaheadController(self.cars,self.lane,self.heuristic)
        self.nstep = NStepLookaheadController(self.cars,self.lane, self.heuristic, 2)
        self.bestfirst = BestFirstController(self.cars,self.lane, self.heuristic)
        self.controller = self.bestfirst


        # self.window = Window(self.screen, self.events, 300, 200, "caption")

        self.grid = Grid(50,50,*self.size)
        self.last_distance_grid_update = time() - 10
        self.update_distance_grid()

        self.done = False

        self.register_events()
        self.spin()

    def setup_pygame(self):
        pygame.init()
         
        # Set the width and height of the screen [width, height]
        self.size = (self.background.rect.width, self.background.rect.height)
        self.screen = pygame.display.set_mode(self.size)

        self.font = pygame.font.SysFont("arial",10)
         
        pygame.display.set_caption("My Game")

    def draw_string(self,string,x,y,color=Draw.BLACK):
        Draw.draw_string(self.screen,self.font,string,x,y,color)


    def draw(self):
        self.background.draw(self.screen)

        # self.grid.draw(self.screen)

        self.lane.draw(self.screen)

        self.camview.draw(self.screen)

        # Draw car
        for car in self.cars:
            if self.controller is not None:
                if hasattr(self.controller,"action"):
                    car.draw(self.screen, self.controller.action)
                self.controller.draw(self.screen, car)

            else:
                car.draw(self.screen)

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
            for car in self.cars:
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
            if self.controller is not None:
                for car in self.cars:
                    if not car.pause:
                        if car.controller is None:
                            car.controller = self.controller
                        action = car.controller.compute_action(car)
                        car.controller.action = action
                        car.forward(action,dt)


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

