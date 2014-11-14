#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import pygame
from copy import copy
import numpy as np
from Node import Node

class Controller(object):
    """docstring for Controller"""
    def __init__(self):
        super(Controller, self).__init__()

    def compute_action(self,car):
        return 0

class HumanController(Controller):
    """docstring for HumanController"""
    def __init__(self):
        super(HumanController, self).__init__()
    
    def compute_action(self,car):
        keys = pygame.key.get_pressed()
        action = 0
        if keys[pygame.K_LEFT]:
            action += 1
        if keys[pygame.K_RIGHT]:
            action -= 1

        return action

class OneStepLookaheadController(Controller):
    """docstring for OneStepLookaheadController"""
    def __init__(self, lane, heuristic):
        super(OneStepLookaheadController, self).__init__()
        self.lane = lane
        self.heuristic = heuristic
        self.timestep = 0.1 # in s

    def compute_action(self,car):
        origin = Node(car)
        best_q = None
        best_actions = list()
        qs = list()
        for a in car.actions:
            node = origin.advance(a,self.timestep)
            q = self.heuristic.evaluate(node)
            if best_q is None:
                best_q = q
            if q == best_q:
                best_actions.append(a)
            if q > best_q:
                best_q = q
                best_actions = [a]

            # print q, a
            qs.append(q)
        # print np.array(qs).std()

        return best_actions[np.random.randint(len(best_actions))]
