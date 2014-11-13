#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from Draw import Draw 
import pygame

class Window(object):
    """docstring for Window"""
    def __init__(self, screen, events, x, y, caption):
        super(Window, self).__init__()
        self.screen = screen
        self.events = events
        self.x = x
        self.y = y
        self.caption = caption

        self.font = pygame.font.SysFont("arial",10)

        self.events.register_callback("mouse_down", self.on_mouse_down)
        self.events.register_callback("mouse_move", self.on_mouse_move)
        self.events.register_callback("mouse_up", self.on_mouse_up)
        self.events.register_callback("mouse_click", self.on_mouse_click)
    
    def draw_string(self,string,x,y,color=Draw.WHITE):
        Draw.draw_string(self.screen,self.font,string,x,y,color)

    def draw(self):
        self.draw_string(self.caption,self.x,self.y-10)
        Draw.draw_gradient_line(self.screen,
            (self.x, self.y), 
            (self.x+50, self.y), 
            (128,128,128), 
            (0,0,0))

    def on_mouse_down(self, args):
        print args
    def on_mouse_move(self, args):
        print args
    def on_mouse_up(self, args):
        print args
    def on_mouse_click(self, args):
        print args
