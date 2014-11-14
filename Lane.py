#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np    
from scipy import interpolate
import math
from Utils import Utils 
from time import time

import pygame
from Draw import Draw

class Lane(object):
    """docstring for ClassName"""
    def __init__(self, events, interval=1,size=6):
        super(Lane, self).__init__()
        self.n_support = 0
        self.n_sampled = 0
        self.support_x = []
        self.support_y = []
        self.sampled_x = []
        self.sampled_y = []
        self.interval = interval
        self.size = size
        self.path_len = 0
        self.highlight_radius = self.size * math.sqrt(2) * 1
        self.highlight = None
        self.selected = None
        self.events = events
        self.last_support_point_move = time()
        self.register_events()

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
        try:
            self.sampled_x, self.sampled_y = self.sample_line()
            diffs = np.sqrt(
                np.square(np.diff(self.sampled_x))+
                np.square(np.diff(self.sampled_y)))
            self.path_len = diffs.sum()
        except Exception, e:
            pass    
        finally:
            pass    
    
        self.n_sampled = len(self.sampled_x)
        self.closest_supports = self.closest_support_idxs(self.sampled_x, self.sampled_y)
        self.events.fire_callbacks("laneupdate", self)

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

    def sample_tangents(self):
        left_shifted_x  = np.hstack([self.sampled_x[-1],self.sampled_x[:-1]]) 
        right_shifted_x = np.hstack([self.sampled_x[1:],self.sampled_x[-1]])
        dx = left_shifted_x - right_shifted_x
        left_shifted_y  = np.hstack([self.sampled_y[-1],self.sampled_y[:-1]]) 
        right_shifted_y = np.hstack([self.sampled_y[1:],self.sampled_y[-1]])
        dy = left_shifted_y - right_shifted_y
        tangents = np.arctan2(dy,dx)*180/math.pi
        # diffs = np.hstack([0,np.diff(tangents)])
        # diffs -= np.round(diffs/360)*360
        # tangents = tangents[0] + diffs.cumsum()
        return tangents

    def register_events(self):
        self.events.init_callback_key("laneupdate")
        self.events.register_callback("mousebuttondown", self.on_mousebuttondown)
        self.events.register_callback("mousemotion", self.on_mousemotion)
        self.events.register_callback("mousebuttonup", self.on_mousebuttonup)

    def on_mousebuttondown(self, event):
        if event.button == 1: # left 
            # select support point
            for (x,y,k) in zip(self.support_x,self.support_y,range(self.n_support)):
                if Utils.distance_between((x,y),event.pos) < self.highlight_radius:
                    self.selected = k


    def on_mousemotion(self, event):
        # highlight
        self.highlight = None
        for (x,y,k) in zip(self.support_x,self.support_y,range(self.n_support)):
            if Utils.distance_between((x,y),event.pos) < self.highlight_radius:
                self.highlight = k

        # move support point
        if self.selected is not None:
            if time() - self.last_support_point_move > 1/60:
                self.last_support_point_move = time()
                self.interval = 5
                self.move_support_point(self.selected, *event.pos)
    
    def on_mousebuttonup(self, event):
        # deselect
        if self.selected is not None:
            self.selected = None
            self.interval = 1
            self.update()

        if event.button == 3: # right
            # add new support point
            first,_ = self.closest_segment(*event.pos)
            closest = self.closest_sampled_idx(*event.pos) 
            self.add_support_point(self.sampled_x[closest],self.sampled_y[closest],first)
    
    def draw(self, screen):
        # Draw the interpolated line
        points = zip(self.sampled_x, self.sampled_y)
        if len(points) > 1:
            pygame.draw.aalines(screen, Draw.WHITE, False, points, 2)

        # Draw support points
        for k in range(self.n_support):
            if self.highlight == k:
                pygame.draw.circle(screen, Draw.HIGHLIGHT, (int(self.support_x[k]),int(self.support_y[k])), int(self.highlight_radius), 0)
            if self.selected == k:
                pygame.draw.rect(screen, Draw.WHITE, self.support_point_rect(k), 2)
            else:
                pygame.draw.rect(screen, Draw.WHITE, self.support_point_rect(k), 1)
            # self.draw_string(k, self.support_x[k],self.support_y[k])
