#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import pygame
from copy import copy
import numpy as np

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
        self.timestep = 100 # in s

    def update(self,car):
        best_q = None
        best_actions = list()
        qs = list()
        for a in car.actions:
            q = self.heuristic.evaluate(copy(car).forward(a,self.timestep))
            if best_q is None:
                best_q = q
            if q == best_q:
                best_actions.append(a)
            if q > best_q:
                best_q = q
                best_actions = [a]

            print q, a
            qs.append(q)
        # print np.array(qs).std()

        self.action = best_actions[np.random.randint(len(best_actions))]
