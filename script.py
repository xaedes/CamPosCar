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

from Lane import Lane
from Controller import *
from Heuristic import Heuristic
from Car import Car
from Grid import Grid
from Draw import Draw
from Window import Window
from Events import Events

import math
from copy import copy
# Define some colors
def inRect(rect, i, j):
    x,y,w,h = rect
    return i >= x and i <= x + w - 1 and  j >= y and j <= y + h - 1

d2r = math.pi / 180


class App(object):
    """docstring for App"""
    def __init__(self):
        super(App, self).__init__()
        
        self.setup_pygame()

        self.lane = Lane()
        self.lane.add_support_point(100,100)
        self.lane.add_support_point(200,100)
        self.lane.add_support_point(200,200)
        self.lane.add_support_point(100,200)


        self.car = Car(x=150,y=100,theta=45)
        self.action = None
        self.human = HumanController()
        self.heuristic = Heuristic(self.lane)
        self.onestep = OneStepLookaheadController(self.lane,self.heuristic)
        self.controller = self.human

        self.events = Events()

        self.window = Window(self.screen, self.events, 300, 200, "caption")

        self.last_support_point_insert_time = time() 

        self.grid = Grid(50,50,*self.size)
        self.update_distance_grid()

        self.spin()

    def setup_pygame(self):
        pygame.init()
         
        # Set the width and height of the screen [width, height]
        self.size = (700, 500)
        self.screen = pygame.display.set_mode(self.size)

        self.font = pygame.font.SysFont("arial",10)
         
        pygame.display.set_caption("My Game")

    def draw_string(self,string,x,y,color=Draw.BLACK):
        Draw.draw_string(self.screen,self.font,string,x,y,color)

    def rotate_points(self,points,angle,at=(0,0)):
        ax, ay = at
        d2r=math.pi/180
        cs,sn=math.cos(angle*d2r),math.sin(angle*d2r)
        return [(ax+(i-ax) * cs - (j-ay) * sn,ay+(i-ax) * sn + (j-ay) * cs) for (i,j) in points]
    
    def translate_points(self,points,x,y):
        return [(i+x,j+y) for (i,j) in points]

    def draw_rotated_rect(self,x,y,w,h,angle,color=Draw.BLACK):
        xs=[-w/2,
           w/2,
           w/2,
           -w/2]

        ys=[-h/2,
           -h/2,
           h/2,
           h/2]

        rotated = self.rotate_points(zip(xs,ys), angle)
        translated = self.translate_points(rotated,x,y)

        pygame.draw.polygon(self.screen, color, translated, 1)


    def draw(self):

        self.grid.draw(self.screen)

        # Draw the interpolated line
        points = zip(self.lane.sampled_x, self.lane.sampled_y)
        if len(points) > 1:
            pygame.draw.aalines(self.screen, Draw.WHITE, False, points, 2)

        # Draw support points
        for k in range(self.lane.n_support):
            if self.lane.highlight == k:
                pygame.draw.circle(self.screen, HIGHLIGHT, (int(self.lane.support_x[k]),int(self.lane.support_y[k])), int(self.lane.highlight_radius), 0)
            if self.lane.selected == k:
                pygame.draw.rect(self.screen, Draw.WHITE, self.lane.support_point_rect(k), 2)
            else:
                pygame.draw.rect(self.screen, Draw.WHITE, self.lane.support_point_rect(k), 1)

            # self.draw_string(k, self.lane.support_x[k],self.lane.support_y[k])

        # Draw car
        self.draw_rotated_rect(self.car.x,self.car.y,self.car.size,self.car.size*0.8,self.car.theta,Draw.WHITE)
        if self.controller is not None and self.controller.action is not None:
            action_lines={}
            m = self.car.size * 1.10
            l = self.car.size * 0.5
            for a in self.car.actions:
                action_line = self.translate_points(self.rotate_points([(0,0),(m,-a*l)],self.car.theta),self.car.x,self.car.y)
                color = Draw.DARKBLUE if self.controller.action == a else Draw.WHITE
                width = 2 if self.controller.action == a else 1
                # print action_line
                pygame.draw.lines(self.screen,color,False,action_line,width)

        self.window.draw()

    
    def distance_between(self, a, b):
        return math.sqrt(np.sum(np.square(np.array(a)-np.array(b))))

    def input(self):
        # get mouse info
        cursor = pygame.mouse.get_pos()
        (left_button, middle_button, right_button) = pygame.mouse.get_pressed() 
        
        # select support points
        if left_button == 1 and self.lane.selected is None:
            # for k in range(self.lane.n_support):
            for (x,y,k) in zip(self.lane.support_x,self.lane.support_y,range(self.lane.n_support)):
                if self.distance_between((x,y),cursor) < self.lane.highlight_radius:
                # if inRect(self.lane.support_point_rect(k),cursor[0],cursor[1]):
                    self.lane.selected = k

        # move support points
        if left_button == 1 and  self.lane.selected is not None:
            self.lane.interval = 5
            self.lane.move_support_point(self.lane.selected, cursor[0], cursor[1])
            self.update_distance_grid()

        keys = pygame.key.get_pressed()
        if self.lane.selected is not None:
            if keys[pygame.K_DELETE]:
                self.lane.remove_support_point(self.lane.selected)
                self.lane.selected = None
                self.update_distance_grid()


        # deselect support points
        if left_button == 0:
            self.lane.selected = None

            if self.lane.interval > 1:
                self.lane.interval = 1
                self.lane.update()

        self.lane.highlight = None
        for (x,y,k) in zip(self.lane.support_x,self.lane.support_y,range(self.lane.n_support)):
            if self.distance_between((x,y),cursor) < self.lane.highlight_radius:
                self.lane.highlight = k
                


        # add new support point
        if right_button==1:
            if time() - self.last_support_point_insert_time > 1:
                first,_ = self.lane.closest_segment(cursor[0],cursor[1])
                closest = self.lane.closest_sampled_idx(cursor[0],cursor[1]) 
                self.lane.add_support_point(self.lane.sampled_x[closest],self.lane.sampled_y[closest],first)
                self.last_support_point_insert_time = time() 
                self.update_distance_grid()


        if keys[pygame.K_SPACE]:
            # save original speed
            if not hasattr(self.car,"speed_on"):
                self.car.speed_on = self.car.speed
            # toggle speed
            self.car.speed = self.car.speed_on - self.car.speed
        
        if keys[pygame.K_RETURN]:
            self.controller = self.human if self.controller != self.human else self.onestep

    def update_distance_grid(self):
        for i in range(self.grid.width):
            for j in range(self.grid.height):
                x,y = self.grid.xs[i], self.grid.ys[j]

                closest_idx = self.lane.closest_sampled_idx(x, y)
                diff = np.array([self.lane.sampled_x[closest_idx]-x,self.lane.sampled_y[closest_idx]-y])
                distance = math.sqrt(np.sum(np.square(diff)))

                self.grid.data[i,j] = distance*distance
        

    def spin(self):
        # Loop until the user clicks the close button.
        done = False
         
        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        self.last_time = time()

        # -------- Main Program Loop -----------
        while not done:
            dt = time()-self.last_time
            self.last_time = time()
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    done = True # Flag that we are done so we exit this loop
            self.input()

            # --- Game logic should go here
            if self.controller is not None:
                self.controller.update(self.car)

                if self.controller.action is not None:
                    self.car.forward(self.controller.action,dt)

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

