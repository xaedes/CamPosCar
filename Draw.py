#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np
import math
import pygame

import scipy.interpolate

from Utils import Utils

class Draw(object):
    """docstring for Draw"""
    BLACK     = (   0,   0,   0)
    WHITE     = ( 255, 255, 255)
    BLUE      = (   0,   0, 255)
    GREEN     = (   0, 255,   0)
    RED       = ( 255,   0,   0)
    DARKBLUE  = (   0,   0, 128)
    GRAY      = ( 128, 128, 128)
    LIGHTGRAY = ( 222, 222, 222)
    # HIGHLIGHT = (   8,   0,  39)
    HIGHLIGHT = ( 247, 255, 216)
    YELLOW    = ( 255, 255,   0)
    
    @classmethod
    def draw_string(CLS, screen,font,string,x,y,color=BLACK):
        rendered = font.render(str(string), True,color)
        screen.blit(rendered,(x,y)) 
        return rendered.get_size()

    @classmethod
    def draw_gradient_line(CLS, screen,point1,point2,color1,color2,interval=1,width=1):
        diff = np.array([point1[0]-point2[0],point1[1]-point2[1]])
        length = math.sqrt(np.sum(np.square(diff)))
        n = int(length / interval)
        points = np.vstack([np.linspace(point1[0],point2[0],n),
                            np.linspace(point1[1],point2[1],n)])
        color1 = np.array(color1)
        color2 = np.array(color2)
        for i in range(n-1):
            color = (color2 - color1)*i/(n-1)+color1
            # print  points[i], points[i+1]
            pygame.draw.line(screen, color, points[:,i], points[:,i+1], width)

    @classmethod
    def draw_rotated_rect(CLS,screen,x,y,w,h,angle,color=BLACK):
        # angle in degree
        # xs=[-w/2,
        #    w/2,
        #    w/2,
        #    -w/2]

        # ys=[-h/2,
        #    -h/2,
        #    h/2,
        #    h/2]

        # rotated = Utils.rotate_points(zip(xs,ys), angle)
        # translated = Utils.translate_points(rotated,x,y)

        pygame.draw.polygon(screen, color, Utils.rotated_rect_points((x,y),angle,w,h), 1)

    @classmethod
    def draw_nparr(CLS, screen, arr, x=0, y=0):
        # Reference pixels into a 3d array
        screen_arr = pygame.surfarray.pixels3d(screen)
        w,h = arr.shape[:2]
        x2,y2 = min(screen_arr.shape[0],x+w),min(screen_arr.shape[1],y+h)
        # blit arr directly into referenced screen pixels
        if len(arr.shape) == 2:
            screen_arr[x:x2,y:y2,0] = arr
            screen_arr[x:x2,y:y2,1] = arr
            screen_arr[x:x2,y:y2,2] = arr
        else:
            screen_arr[x:x2,y:y2,:] = arr