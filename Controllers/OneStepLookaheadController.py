#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from NodeController import NodeController
from Node import Node
from Draw import Draw
import pygame
import numpy as np


class OneStepLookaheadController(NodeController):
    """docstring for OneStepLookaheadController"""
    def __init__(self, lane, heuristic):
        super(OneStepLookaheadController, self).__init__()
        self.lane = lane
        self.heuristic = heuristic
        self.timestep = 0.1 # in s

    def compute_action_from_node(self, origin):
        best_q = None
        best_actions = list()
        for a in origin.car.actions:
            node = origin.advance(a,self.timestep)
            q = self.heuristic.evaluate(node)
            if best_q is None:
                best_q = q
            if q == best_q:
                best_actions.append(a)
            if q > best_q:
                best_q = q
                best_actions = [a]

        return best_actions[np.random.randint(len(best_actions))]


    def draw_node(self, screen, node):
        for child in node.children:
            pygame.draw.line(screen, Draw.WHITE, (node.car.x, node.car.y), (child.car.x,child.car.y), 1)
