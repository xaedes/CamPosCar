#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np
import math
import pygame

import scipy.interpolate

class Draw(object):
    """docstring for Draw"""
    BLACK     = (   0,   0,   0)
    WHITE     = ( 255, 255, 255)
    GREEN     = (   0, 255,   0)
    RED       = ( 255,   0,   0)
    DARKBLUE  = (   0,   0, 128)
    LIGHTGRAY = ( 222, 222, 222)
    HIGHLIGHT = ( 247, 255, 216)
    
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
