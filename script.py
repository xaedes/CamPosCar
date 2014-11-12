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
drag_and_drop_support_point = False
selected_support_point = None
x=[100,200,200,100]
y=[100,100,200,200]
x = x 
y = y 

def sampleLine(support_x,support_y,interval=1):
    # sample some points to determine path length

    tck,u=interpolate.splprep([support_x+support_x[0:1],support_y+support_y[0:1]],s=0.0,per=1)
    x_i,y_i= interpolate.splev(np.linspace(0,1,50),tck)
    diffs = np.sqrt(np.square(np.diff(x_i))+np.square(np.diff(y_i)))
    path_len = diffs.sum()
    # we want to sample the points so that the distance between neighboring points is just interval
    # so sample round(path_len) points
    x_i,y_i= interpolate.splev(np.linspace(0,1,round(path_len/interval)),tck)
    return x_i,y_i

x_i,y_i = sampleLine(x,y)

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

def inRect(rect, i, j):
    x,y,w,h = rect
    return i >= x and i <= x + w - 1 and  j >= y and j <= y + h - 1

def closestPointIdx(points_x,points_y, x, y):
    # get closest point in (points_x,points_y) too (x,y)
    distances = np.sqrt(np.square(points_x-x)+np.square(points_y-y))
    closest_idx = np.argmin(distances)
    print closest_idx
    return closest_idx

def closestSupportPointIdx(support_x,support_y,x,y):
    return closestPointIdx(support_x,support_y,x,y)

def closestSupportPointIdxs(support_x,support_y,xs,ys):
    return [closestSupportPointIdx(support_x,support_y,x,y) for x,y in zip(xs,ys)]

closestSupport = closestSupportPointIdxs(x,y,x_i,y_i)

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
    if left_button == 1 and not drag_and_drop_support_point:
        for (k,i,j) in zip(range(len(x)),x,y):
            if inRect(supportPointRect(i,j),cursor[0],cursor[1]):
                drag_and_drop_support_point = True
                selected_support_point = k

    # move support points
    if left_button == 1 and drag_and_drop_support_point and selected_support_point is not None:
        x[selected_support_point] = cursor[0]
        y[selected_support_point] = cursor[1]
        x_i,y_i = sampleLine(x,y)
        closestSupport = closestSupportPointIdxs(x,y,x_i,y_i)


    # deselect support points
    if left_button == 0:
        drag_and_drop_support_point = False
        selected_support_point = None
 
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
    for (k,i,j) in zip(range(len(x)),x,y):
        if selected_support_point == k:
            pygame.draw.rect(screen, BLACK, supportPointRect(i,j), 2)
        else:
            pygame.draw.rect(screen, BLACK, supportPointRect(i,j), 1)

    # Draw line from mouse to closest point line
    closest = closestPointIdx(x_i,y_i,cursor[0],cursor[1])
    pygame.draw.aaline(screen, BLACK, 
        (cursor[0],cursor[1]), 
        (x_i[closest],y_i[closest]))

    # highlight support point that is nearest to closest
    pygame.draw.rect(screen, BLACK, supportPointRect(x[closestSupport[closest]],y[closestSupport[closest]]), 2)

    # draw line from closest support point to closest
    closestSuppIdx=closestPointIdx(x_i,y_i,x[closestSupport[closest]],y[closestSupport[closest]])
    highlight = points[min(closestSuppIdx,closest):max(closestSuppIdx,closest)+1]
    if len(highlight) > 1:
        pygame.draw.aalines(screen, RED, False, highlight, 6)

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()