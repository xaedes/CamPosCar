#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from Controller import Controller

class ActionController(Controller):
    """docstring for ActionController"""
    def __init__(self):
        super(ActionController, self).__init__()

    def update(self, car, dt):
        self.action = self.compute_action(car)
        car.forward(self.action,dt)

    def compute_action(self,car):
        return 0

    def draw(self, screen, car):
        pass


