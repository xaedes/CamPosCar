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
from scipy import interpolate

class Lane(object):
    """docstring for ClassName"""
    def __init__(self, interval=1,size=6):
        super(Lane, self).__init__()
        self.n_support = 0
        self.n_sampled = 0
        self.support_x = []
        self.support_y = []
        self.sampled_x = []
        self.sampled_y = []
        self.interval = interval
        self.size = size
        self.selected = None

    def add_support_point(self, x,y,before=-1):
        self.support_x = self.support_x[:before+1] + [x] + self.support_x[before+1:]
        self.support_y = self.support_y[:before+1] + [y] + self.support_y[before+1:]
        self.n_support+=1
        self.update()

    def remove_support_point(self, index):
        self.support_x = self.support_x[:index]+self.support_x[index+1:]
        self.support_y = self.support_y[:index]+self.support_y[index+1:]
        self.n_support-=1
        self.update()

    def move_support_point(self,index,x,y):
        self.support_x[index]=x
        self.support_y[index]=y
        self.update()

    def update(self):
        self.sampled_x, self.sampled_y = self.sample_line()
        self.n_sampled = len(self.sampled_x)
        self.closest_supports = self.closest_support_idxs(self.sampled_x, self.sampled_y)

    def sample_line(self, interval = None):
        if interval is None:
            interval = self.interval
        if self.n_support < 3:
            return [],[]
        # sample some points to determine path length

        tck,u=interpolate.splprep([
            self.support_x+self.support_x[0:1],
            self.support_y+self.support_y[0:1]],s=0.0,per=1)
        x_i,y_i= interpolate.splev(np.linspace(0,1,50),tck)
        diffs = np.sqrt(np.square(np.diff(x_i))+np.square(np.diff(y_i)))
        path_len = diffs.sum()
        # we want to sample the points so that the distance between neighboring points is just interval
        # so sample round(path_len) points
        x_i,y_i= interpolate.splev(np.linspace(0,1,round(path_len/interval)),tck)
        return x_i,y_i

    def support_point_rect(self,index):
        return [self.support_x[index]-self.size/2, self.support_y[index]-self.size/2, self.size, self.size]

    def closest_idx(self,points_x,points_y, to_x, to_y):
        # get closest point in (points_x,points_y) to (to_x, to_y)
        distances = np.sqrt(np.square(points_x-to_x)+np.square(points_y-to_y))
        return np.argmin(distances)

    def closest_sampled_idx(self,x, y):
        return self.closest_idx(self.sampled_x,self.sampled_y,x,y)

    def closest_support_idx(self,x,y):
        return self.closest_idx(self.support_x,self.support_y,x,y)

    def closest_support_idxs(self,xs,ys):
        return [self.closest_support_idx(x,y) for x,y in zip(xs,ys)]

    def closest_segment(self,x,y):
        closest_sampled = self.closest_sampled_idx(x,y)
        closest_sampled_of_closest_support = self.closest_sampled_idx(
            self.support_x[self.closest_supports[closest_sampled]],
            self.support_y[self.closest_supports[closest_sampled]])
        # find first support point of the closest segment
        if self.closest_supports[closest_sampled] == 0 and closest_sampled > self.n_sampled/2:
            # last segment
            first = self.n_support - 1
            second = 0
        else:
            # any other segment
            if closest_sampled_of_closest_support > closest_sampled:
                first = self.closest_supports[closest_sampled] - 1
            else:
                first = self.closest_supports[closest_sampled]

            second = first + 1

        return first,second



lane = Lane()
lane.add_support_point(100,100)
lane.add_support_point(200,100)
lane.add_support_point(200,200)
lane.add_support_point(100,200)



# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
 
pygame.init()
 
# Set the width and height of the screen [width, height]
size = (700, 500)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("My Game")
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

def inRect(rect, i, j):
    x,y,w,h = rect
    return i >= x and i <= x + w - 1 and  j >= y and j <= y + h - 1

last_support_point_insert_time = time() 

# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
    # get mouse info
    cursor = pygame.mouse.get_pos()
    (left_button, middle_button, right_button) = pygame.mouse.get_pressed() 
    
    # select support points
    if left_button == 1 and lane.selected is None:
        for k in range(lane.n_support):
            if inRect(lane.support_point_rect(k),cursor[0],cursor[1]):
                lane.selected = k

    # move support points
    if left_button == 1 and  lane.selected is not None:
        lane.move_support_point(lane.selected, cursor[0], cursor[1])

    keys = pygame.key.get_pressed()
    if lane.selected is not None:
        if keys[pygame.K_DELETE]:
            lane.remove_support_point(lane.selected)
            lane.selected = None

    # deselect support points
    if left_button == 0:
        lane.selected = None

    # add new support point
    if right_button==1:
        if time() - last_support_point_insert_time > 1:
            first,_ = lane.closest_segment(cursor[0],cursor[1])
            closest = lane.closest_sampled_idx(cursor[0],cursor[1]) 
            lane.add_support_point(lane.sampled_x[closest],lane.sampled_y[closest],first)
            last_support_point_insert_time = time() 

    # --- Game logic should go here
 
    # --- Drawing code should go here
 
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
 
    # Draw the interpolated line
    points = zip(lane.sampled_x, lane.sampled_y)
    pygame.draw.aalines(screen, BLACK, False, points, 2)

    # Draw support points
    for k in range(lane.n_support):
        if lane.selected == k:
            pygame.draw.rect(screen, BLACK, lane.support_point_rect(k), 2)
        else:
            pygame.draw.rect(screen, BLACK, lane.support_point_rect(k), 1)

    
    
    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()