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

from scipy import interpolate
x=[100,200,200,100,100]
y=[100,100,200,200,100]
tck,u=interpolate.splprep([x,y],s=0.0)

# sample some points to determine path length
x_i,y_i= interpolate.splev(np.linspace(0,1,50),tck)
diffs = np.sqrt(np.square(np.diff(x_i))+np.square(np.diff(y_i)))
path_len = diffs.sum()
# we want to sample the points so that the distance between neighboring points is just 1
# so sample round(path_len) points
x_i,y_i= interpolate.splev(np.linspace(0,1,round(path_len)),tck)
diffs = np.sqrt(np.square(np.diff(x_i))+np.square(np.diff(y_i)))


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

def supportPointRect(i,j):
	return [i-support_point_size_half, j-support_point_size_half, support_point_size, support_point_size]
 
# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
 
    # --- Game logic should go here
 
    # --- Drawing code should go here
 
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
 
    # Draw the interpolated line
    points = zip(x_i, y_i)
    pygame.draw.aalines(screen, BLACK, False, points, 2)

    # Draw support points
    support_point_size = 6
    support_point_size_half = 3
    for (i,j) in zip(x,y):
    	pygame.draw.rect(screen, BLACK, supportPointRect(i,j), 1)

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()