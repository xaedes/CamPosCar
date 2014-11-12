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
        lane.interval = 5
        lane.move_support_point(lane.selected, cursor[0], cursor[1])

    keys = pygame.key.get_pressed()
    if lane.selected is not None:
        if keys[pygame.K_DELETE]:
            lane.remove_support_point(lane.selected)
            lane.selected = None

    # deselect support points
    if left_button == 0:
        lane.selected = None

        if lane.interval > 1:
            lane.interval = 1
            lane.update()

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