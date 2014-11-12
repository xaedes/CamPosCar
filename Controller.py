#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import pygame

class Controller(object):
    """docstring for Controller"""
    def __init__(self):
        super(Controller, self).__init__()
        self.action = None

    def update(self):
        pass

class HumanController(Controller):
    """docstring for HumanController"""
    def __init__(self):
        super(HumanController, self).__init__()
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.action = 0
        if keys[pygame.K_LEFT]:
            self.action += 1
        if keys[pygame.K_RIGHT]:
            self.action -= 1