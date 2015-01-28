#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from ActionController import ActionController
from Node import Node


class NodeController(ActionController):
    """docstring for OneStepLookaheadController"""
    def __init__(self, all_cars):
        super(NodeController, self).__init__()
        self.origins = dict()
        self.all_cars = all_cars

    def compute_action_from_node(self, origin):
        return 0

    def compute_other_cars(self, car):
        return [other for other in self.all_cars if other.id != car.id]

    def compute_action(self,car):
        origin = Node(car,other_cars=self.compute_other_cars(car))
        self.origins[car.id] = origin
        action = self.compute_action_from_node(origin)
        return action

    def draw_node(self, screen, origin):
        pass 

    def draw(self, screen, car):
        if car.id in self.origins:
            origin = self.origins[car.id]
            stack = [origin]
            while len(stack) > 0:
                current = stack.pop()

                self.draw_node(screen, current)

                for child in current.children:
                    stack.append(child)
