#!/usr/bin/env python
# -*- coding: utf-8 -*-
from copy import copy

class Node(object):
    heuristic = None
    """docstring for Node"""
    def __init__(self, car, action=None, prevNode = None,other_cars=None):
        super(Node, self).__init__()
        self.car = car
        self.action = action
        self.prevNode = prevNode
        self.children = []
        self.other_cars = other_cars if other_cars is not None else []
        if self.prevNode is not None:
            self.action_history = copy(self.prevNode.action_history)
            self.heuristic_history = copy(self.prevNode.heuristic_history)
        else:
            self.action_history = []
            self.heuristic_history = []
        if action is not None:
            self.action_history.append(action)

        self.heuristic_value = Node.heuristic.evaluate(self)
        self.best_heuristic_value_from_here = self.heuristic_value
        self.heuristic_history.append(self.heuristic_value)

        if self.prevNode is not None:
            self.depth = self.prevNode.depth + 1
            self.prevNode.children.append(self)

            # propagate heuristic value to parents
            current = self
            while current.prevNode is not None:
                current.prevNode.best_heuristic_value_from_here = max(
                    current.prevNode.best_heuristic_value_from_here,
                    current.best_heuristic_value_from_here)
                current = current.prevNode

        else:
            self.depth = 0


    def advance(self, action, timestep):
        return Node(
                car = copy(self.car).forward(action,timestep), 
                action = action, 
                prevNode = self,
                other_cars = [copy(car).forward(0,timestep) for car in self.other_cars])

    def advance_all(self, timestep):
        return [self.advance(action, timestep) for action in self.car.actions]
