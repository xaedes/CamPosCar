#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import pygame
from copy import copy

class Controller(object):
    """docstring for Controller"""
    def __init__(self):
        super(Controller, self).__init__()
        self.action = None

    def update(self,car):
        pass

class HumanController(Controller):
    """docstring for HumanController"""
    def __init__(self):
        super(HumanController, self).__init__()
    
    def update(self,car):
        keys = pygame.key.get_pressed()
        self.action = 0
        if keys[pygame.K_LEFT]:
            self.action += 1
        if keys[pygame.K_RIGHT]:
            self.action -= 1

class OneStepLookaheadController(Controller):
    """docstring for OneStepLookaheadController"""
    def __init__(self, lane, heuristic):
        super(OneStepLookaheadController, self).__init__()
        self.lane = lane
        self.heuristic = heuristic
        self.timestep = 0.1 # in s

    def update(self,car):
        best_q = None
        best_action = None
        for a in car.actions:
            q = self.heuristic.evaluate(copy(car).forward(a,self.timestep))
            if best_q is None or q > best_q:
                best_q = q
                best_action = a

        self.action = best_action
