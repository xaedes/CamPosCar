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
import math

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
 
def inRect(rect, i, j):
    x,y,w,h = rect
    return i >= x and i <= x + w - 1 and  j >= y and j <= y + h - 1


class Car(object):
    """docstring for Car"""
    def __init__(self, x, y, theta, speed=1, size=10):
        super(Car, self).__init__()
        self.x = x
        self.y = y
        self.theta = theta # in degree
        self.size = size
        self.speed = speed # px / s
        # self.theta_rate =  10 # in degree/s

    # def forward(self,action,dt):
    #     assert action in [-1,0,1]
    #     # action == -1  : left
    #     # action ==  0  : middle
    #     # action ==  1  : right
    #     vx = math.cos(self.theta) * self.speed * dt
    #     vy = math.sin(self.theta) * self.speed * dt
    #     self.x += vx
    #     self.y += vy
    #     self.theta -= self.theta_rate * dt * action



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

        self.last_support_point_insert_time = time() 

        self.spin()

    def setup_pygame(self):
        pygame.init()
         
        # Set the width and height of the screen [width, height]
        self.size = (700, 500)
        self.screen = pygame.display.set_mode(self.size)

        self.font = pygame.font.SysFont("calibri",40)
         
        pygame.display.set_caption("My Game")

    def draw_string(self,string,x,y,color=BLACK):
        rendered = self.font.render(str(string), True,color)
        self.screen.blit(rendered,(x,y))

    def rotate_points(self,points,angle):
        d2r=math.pi/180
        cs,sn=math.cos(angle*d2r),math.sin(angle*d2r)
        return [(i * cs - j * sn,i * sn + j * cs) for (i,j) in points]
    def translate_points(self,points,x,y):
        return [(i+x,j+y) for (i,j) in points]

    def draw_rotated_rect(self,x,y,w,h,angle,color=BLACK):
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
        # Draw the interpolated line
        points = zip(self.lane.sampled_x, self.lane.sampled_y)
        pygame.draw.aalines(self.screen, BLACK, False, points, 2)

        # Draw support points
        for k in range(self.lane.n_support):
            if self.lane.selected == k:
                pygame.draw.rect(self.screen, BLACK, self.lane.support_point_rect(k), 2)
            else:
                pygame.draw.rect(self.screen, BLACK, self.lane.support_point_rect(k), 1)

            self.draw_string(k, self.lane.support_x[k],self.lane.support_y[k])

        # Draw car
        self.draw_rotated_rect(self.car.x,self.car.y,self.car.size*0.8,self.car.size,self.car.theta)

    def input(self):
        # get mouse info
        cursor = pygame.mouse.get_pos()
        (left_button, middle_button, right_button) = pygame.mouse.get_pressed() 
        
        # select support points
        if left_button == 1 and self.lane.selected is None:
            for k in range(self.lane.n_support):
                if inRect(self.lane.support_point_rect(k),cursor[0],cursor[1]):
                    self.lane.selected = k

        # move support points
        if left_button == 1 and  self.lane.selected is not None:
            self.lane.interval = 5
            self.lane.move_support_point(self.lane.selected, cursor[0], cursor[1])

        keys = pygame.key.get_pressed()
        if self.lane.selected is not None:
            if keys[pygame.K_DELETE]:
                self.lane.remove_support_point(self.lane.selected)
                self.lane.selected = None

        # deselect support points
        if left_button == 0:
            self.lane.selected = None

            if self.lane.interval > 1:
                self.lane.interval = 1
                self.lane.update()

        # add new support point
        if right_button==1:
            if time() - self.last_support_point_insert_time > 1:
                first,_ = self.lane.closest_segment(cursor[0],cursor[1])
                closest = self.lane.closest_sampled_idx(cursor[0],cursor[1]) 
                self.lane.add_support_point(self.lane.sampled_x[closest],self.lane.sampled_y[closest],first)
                self.last_support_point_insert_time = time() 

    def spin(self):
        # Loop until the user clicks the close button.
        done = False
         
        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        

        # -------- Main Program Loop -----------
        while not done:
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    done = True # Flag that we are done so we exit this loop
            self.input()

            # --- Game logic should go here
         
            # --- Drawing code should go here
         
            # First, clear the screen to white. Don't put other drawing commands
            # above this, or they will be erased with this command.
            self.screen.fill(WHITE)
         
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

