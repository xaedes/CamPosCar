#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

import pygame

class Events(object):
    """docstring for Events"""
    def __init__(self):
        super(Events, self).__init__()
        self.callbacks = dict()
        self.pygame_mappings = dict({
            pygame.QUIT: "quit",
            pygame.ACTIVEEVENT: "activeevent",
            pygame.KEYDOWN: "keydown",
            pygame.KEYUP: "keyup",
            pygame.MOUSEMOTION: "mousemotion",
            pygame.MOUSEBUTTONUP: "mousebuttonup",
            pygame.MOUSEBUTTONDOWN: "mousebuttondown",
            pygame.JOYAXISMOTION: "joyaxismotion",
            pygame.JOYBALLMOTION: "joyballmotion",
            pygame.JOYHATMOTION: "joyhatmotion",
            pygame.JOYBUTTONUP: "joybuttonup",
            pygame.JOYBUTTONDOWN: "joybuttondown",
            pygame.VIDEORESIZE: "videoresize",
            pygame.VIDEOEXPOSE: "videoexpose",
            pygame.USEREVENT: "userevent"
            })

    def init_callback_key(self, key):
        self.callbacks[key] = []

    def register_callback(self, key, callback):
        if key not in self.callbacks:
            self.init_callback_key(key)

        if callback not in self.callbacks[key]:
            self.callbacks[key].append(callback)

    def fire_callbacks(self, key, args):
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                callback(args)
