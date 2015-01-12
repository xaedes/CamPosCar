#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame

class Background(object):
    """docstring for ClassName"""
    def __init__(self, filename):
        super(Background, self).__init__()
        self.filename = filename
        self.img = pygame.image.load(self.filename)
        # self.pixelArray = pygame.PixelArray(self.img)
        # help(self.pixelArray)
        self.rect = self.img.get_rect()

    def draw(self, screen):
    	screen.blit(self.img, self.rect)