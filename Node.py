#!/usr/bin/env python
# -*- coding: utf-8 -*-
from copy import copy

class Node(object):
    heuristic = None
    """docstring for Node"""
    def __init__(self, car, action=None, prevNode = None):
        super(Node, self).__init__()
        self.car = car
        self.action = action
        self.prevNode = prevNode
        self.children = []
        if Node.heuristic is not None:
            self.heuristic_value = Node.heuristic.evaluate(self)
        else:
            self.heuristic_value = None

        self.best_heuristic_value_from_here = self.heuristic_value

        if self.prevNode is not None:
            self.depth = self.prevNode.depth + 1
            self.prevNode.children.append(self)

            # propagate heuristic value to parents
            if self.heuristic_value is not None:
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
                prevNode = self)

    def advance_all(self, timestep):
        return [self.advance(action, timestep) for action in self.car.actions]
