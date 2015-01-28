#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from Controller import Controller
from Utils import Utils

class INSGhostController(Controller):
    """docstring for INSGhostController"""
    def __init__(self, ins):
        super(INSGhostController, self).__init__()
        self.ins = ins

    def update(self, car, dt):
        # follow ins estimate
        car.x = self.ins.get_state('pos_x')
        car.y = self.ins.get_state('pos_y')
        car.speed = self.ins.get_state('speed')
        car.theta = self.ins.get_state('orientation') / Utils.d2r

    def draw(self, screen, car):
        pass


