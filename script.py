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

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
 
def inRect(rect, i, j):
    x,y,w,h = rect
    return i >= x and i <= x + w - 1 and  j >= y and j <= y + h - 1

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

        self.last_support_point_insert_time = time() 

        self.spin()

    def setup_pygame(self):
        pygame.init()
         
        # Set the width and height of the screen [width, height]
        self.size = (700, 500)
        self.screen = pygame.display.set_mode(self.size)
         
        pygame.display.set_caption("My Game")
    
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

