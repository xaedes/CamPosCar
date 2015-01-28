#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

class Controller(object):
    """docstring for Controller"""
    def __init__(self):
        super(Controller, self).__init__()

    def update(self, car, dt):
        pass

    def draw(self, screen, car):
        pass


