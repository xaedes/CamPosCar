#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from ActionController import ActionController

import pygame

class HumanController(ActionController):
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

    def draw(self, screen, car):
        pass