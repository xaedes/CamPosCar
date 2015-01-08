#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from NodeController import NodeController
from Node import Node
from Draw import Draw
import pygame
import numpy as np
from time import time

from Queue import PriorityQueue

class BestFirstController(NodeController):
    def __init__(self, all_cars,lane, heuristic):
        super(BestFirstController, self).__init__(all_cars)
        self.lane = lane
        self.heuristic = heuristic
        self.timestep = 4/60 # in s

    def compute_action_from_node(self, origin):
        start = time()

        pqueue = PriorityQueue()
        pqueue.put((-origin.heuristic_value,origin))
        n_traversed = 0
        while not pqueue.empty():
            _,current = pqueue.get()
            n_traversed += 1
            # if current.heuristic_value <= -1e10:
                # continue
                
            if time() - start < 1/(60*2):
                children = current.advance_all(self.timestep)
                children = sorted(children, key = lambda node:node.heuristic_value)
                for child in children:
                    pqueue.put((-child.heuristic_value,child))

        pqueue = None

        best_q = None
        best_actions = list()
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

        if len(best_actions) == 0:
            return 0
        else:
            return best_actions[np.random.randint(len(best_actions))]

    def draw_node(self, screen, node):
        color = Draw.BLACK
        if node.prevNode is not None:
            current_pos = (node.car.x, node.car.y)
            parent_pos = (node.prevNode.car.x,node.prevNode.car.y)
            pygame.draw.line(screen, color, current_pos, parent_pos, 1)
