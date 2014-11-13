#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import \
    division  # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np  # Numpy, das Number One Number Crunching Tool
import math


class Heuristic(object):
    """docstring for Heuristic"""

    def __init__(self, lane):
        super(Heuristic, self).__init__()
        self.lane = lane
        self.traveled = None

    def evaluate(self, node):
        score = 0
        closest_idx = self.lane.closest_sampled_idx(node.car.x, node.car.y)

        # initialize odometry
        if self.traveled is None:
            self.traveled = closest_idx

        # update odometry
        # diff = closest_idx - self.traveled
        # print "diff", np.round(diff / self.lane.path_len)
        # diff -= np.round(diff / self.lane.path_len) * self.lane.path_len
        # self.traveled += diff
        # score += self.traveled 
        # print self.traveled 

        diff = np.array([self.lane.sampled_x[closest_idx]-node.car.x,self.lane.sampled_y[closest_idx]-node.car.y])
        distance = math.sqrt(np.sum(np.square(diff)))
        # print distance
        score -= distance*distance * 10

        # tangents = self.lane.sample_tangents()
        # print tangents 
        # print car.theta , tangents[closest_idx]
        # diff = car.theta - tangents[closest_idx]
        # diff -= np.round(diff / 360) * 360
        # print diff
        # score -= (diff*diff)
        # print tangents[closest_idx] 

        # pri

        return score
