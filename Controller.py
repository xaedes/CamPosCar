#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import pygame
from copy import copy
import numpy as np
from Node import Node
from Draw import Draw

from time import time

class Controller(object):
    """docstring for Controller"""
    def __init__(self):
        super(Controller, self).__init__()

    def compute_action(self,car):
        return 0

    def draw(self, car):
        pass

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

    def draw(self, car):
        pass

class OneStepLookaheadController(Controller):
    """docstring for OneStepLookaheadController"""
    def __init__(self, lane, heuristic):
        super(OneStepLookaheadController, self).__init__()
        self.lane = lane
        self.heuristic = heuristic
        self.timestep = 0.1 # in s
        self.origins = dict()

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
        self.origins[car.id] = origin
        return best_actions[np.random.randint(len(best_actions))]

    def draw(self, screen, car):
        if car.id in self.origins:
            origin = self.origins[car.id]
            for child in origin.children:
                pygame.draw.line(screen, Draw.WHITE, (origin.car.x, origin.car.y), (child.car.x,child.car.y), 1)

class NStepLookaheadController(Controller):
    def __init__(self, lane, heuristic, n = 4):
        super(NStepLookaheadController, self).__init__()
        self.lane = lane
        self.heuristic = heuristic
        self.timestep = 4/60 # in s
        self.n = n
        self.origins = dict()

    def compute_action(self,car):
        origin = Node(car)

        stack = [origin]

        start = time()

        i = 0
        while len(stack) > 0:
            current = stack.pop()
            i += 1
            if current.heuristic <= -1e10:
                continue
                
            if time() - start < 1/(60*4):
                children = current.advance_all(self.timestep)
                children = sorted(children, key = lambda node:node.heuristic_value)
                for child in children:
                    stack.append(child)

        stack = []

        best_q = None
        best_actions = list()
        # qs = list()
        for node in origin.children:
            q = node.heuristic_value
            if best_q is None:
                best_q = q
                best_actions.append(node.action)
            elif abs(q - best_q) < 1e-7: # float approx equal
                best_actions.append(node.action)
            elif q > best_q:
                best_q = q
                best_actions = [node.action]

            # print q, a
            # qs.append(q)
        # print np.array(qs).std()

        self.origins[car.id] = origin

        if len(best_actions) == 0:
            return 0
        else:
            return best_actions[np.random.randint(len(best_actions))]

    def draw(self, screen, car):
        if car.id in self.origins:
            origin = self.origins[car.id]
            stack = [origin]
            max_depth = 0
            while len(stack) > 0:
                current = stack.pop()
                max_depth = max(max_depth, current.depth)
                if current.prevNode is not None:
                    current_pos = (current.car.x, current.car.y)
                    parent_pos = (current.prevNode.car.x,current.prevNode.car.y)
                    # print current_pos, parent_pos
                    pygame.draw.line(screen, Draw.YELLOW, current_pos, parent_pos, 1)
                for child in current.children:
                    stack.append(child)
            print max_depth
