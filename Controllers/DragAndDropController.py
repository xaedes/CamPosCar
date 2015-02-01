#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from time import time
from Controller import Controller
from Utils import Utils

class DragAndDropController(Controller):
    """docstring for DragAndDropController"""
    def __init__(self, events):
        super(DragAndDropController, self).__init__()
        self.events = events
        self.register_events()
        self.cars = set()
        self.selected = None
        self.highlight = None
        self.last_move = time()

    def update(self, car, dt):
        if car not in self.cars:
            self.cars.add(car)
        car.x = car.x
        car.y = car.y
        car.theta = car.theta

    def draw(self, screen, car):
        pass

    def register_events(self):
        self.events.register_callback("mousebuttondown", self.on_mousebuttondown)
        self.events.register_callback("mousemotion", self.on_mousemotion)
        self.events.register_callback("mousebuttonup", self.on_mousebuttonup)



    def on_mousebuttondown(self, event):
        if event.button == 1: # left 
            # select support point
            for (car,x,y) in [(car,car.x, car.y) for car in self.cars]:
                if Utils.distance_between((x,y),event.pos) < car.collision_radius():
                    self.selected = car


    def on_mousemotion(self, event):
        # highlight
        self.highlight = None
        for (car,x,y) in [(car,car.x, car.y) for car in self.cars]:
            if Utils.distance_between((x,y),event.pos) < car.collision_radius():
                self.highlight = car

        # move selected car
        if self.selected is not None:
            if time() - self.last_move > 1/60:
                self.last_move = time()
                self.selected.x = event.pos[0]
                self.selected.y = event.pos[1]
    
    def on_mousebuttonup(self, event):
        # deselect
        if self.selected is not None:
            self.selected = None

        # if event.button == 3: # right
        #     # add new support point
        #     first,_ = self.closest_segment(*event.pos)
        #     closest = self.closest_sampled_idx(*event.pos) 
        #     self.add_support_point(self.sampled_x[closest],self.sampled_y[closest],first)

