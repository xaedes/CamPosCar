#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import math
class Heuristic(object):
	"""docstring for Heuristic"""
	def __init__(self, lane):

		super(Heuristic, self).__init__()
		self.lane = lane

	def evaluate(self, car):
		score = 0
		closest = self.lane.closest_sampled_idx(car.x,car.y)
		closest = np.array(self.lane.sampled_x[closest], self.lane.sampled_y[closest])
		distance = math.sqrt(np.sum(np.square(closest-np.array([car.x,car.y]))))

		score -= distance

		return score
