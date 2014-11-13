#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import math
import pygame

class Grid(object):
	"""docstring for Grid"""
	def __init__(self, width, height, pixel_width, pixel_height):
		super(Grid, self).__init__()
		self.pixel_width = pixel_width
		self.pixel_height = pixel_height
		self.width = width
		self.height = height
		self.cell_pixel_width = self.pixel_width / self.width
		self.cell_pixel_height = self.pixel_height / self.height
		self.data = np.zeros(shape=(self.width,self.height))
		self.xs = np.linspace(self.cell_pixel_width / 2,self.pixel_width-self.cell_pixel_width / 2,self.width)
		self.ys = np.linspace(self.cell_pixel_height / 2,self.pixel_height-self.cell_pixel_height / 2,self.height)

	def cell_rect(self,x,y):
		return (
			math.floor(x*self.cell_pixel_width),
			math.floor(y*self.cell_pixel_height),
			math.ceil(self.cell_pixel_width),
			math.ceil(self.cell_pixel_height))

	def draw(self, screen):
		max_value = np.max(self.data)
		min_value = np.min(self.data)
		for x in range(self.width):
			for y in range(self.height):
				normalized_value = (self.data[x,y] - min_value) / (max_value-min_value)
				color=(normalized_value*255,0,0)
				pygame.draw.rect(screen, color, self.cell_rect(x,y), 0)