#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from Draw import Draw 
from Utils import Utils 
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
        self.caption_size = (0,0)

        self.font = pygame.font.SysFont("arial",10)

        self.draganddrop = False

        self.events.register_callback("mousebuttondown", self.on_mousebuttondown)
        self.events.register_callback("mousemotion", self.on_mousemotion)
        self.events.register_callback("mousebuttonup", self.on_mousebuttonup)
        self.events.register_callback("mousebuttonclick", self.on_mousebuttonclick)
    
    def draw_string(self,string,x,y,color=Draw.WHITE):
        return Draw.draw_string(self.screen,self.font,string,x,y,color)

    def draw(self):
        self.caption_size = self.draw_string(self.caption,self.x,self.y-10)
        Draw.draw_gradient_line(self.screen,
            (self.x, self.y), 
            (self.x+50, self.y), 
            (128,128,128), 
            (0,0,0))

    def get_dragandrop_rect(self):
        return (self.x,self.y-self.caption_size[1],self.caption_size[0],self.caption_size[1])

    def on_mousebuttondown(self, event):
        if event.button == 1:
            if Utils.inRect(self.get_dragandrop_rect(),*event.pos):
                self.draganddrop = True

    def on_mousemotion(self, event):
        if self.draganddrop:
            self.x += event.rel[0]
            self.y += event.rel[1]
    def on_mousebuttonup(self, event):
        self.draganddrop = False

    def on_mousebuttonclick(self, event):
        # print event
        pass
