#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import \
    division  # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np  # Numpy, das Number One Number Crunching Tool
import math

from Utils import Utils

class Heuristic(object):
    """docstring for Heuristic"""

    def __init__(self, lane, cars):
        super(Heuristic, self).__init__()
        self.lane = lane
        self.cars = cars
        self.traveled = None

    def evaluate(self, node):
        score = 0
        node.closest_lane_idx = self.lane.closest_sampled_idx(node.car.x, node.car.y)

        # initialize odometry
        if self.traveled is None:
            self.traveled = node.closest_lane_idx



        # update odometry
        if node.prevNode is not None:
            diff = node.closest_lane_idx - node.prevNode.closest_lane_idx
            # diff -= np.round(diff / self.lane.path_len) * self.lane.path_len
        # print "diff", np.round(diff / self.lane.path_len)
        # self.traveled += diff
            score += diff * -100 
        # print self.traveled 

        score -= 50 * np.array(node.action_history).std()


        distance = Utils.distance_between(
                    (self.lane.sampled_x[node.closest_lane_idx],self.lane.sampled_y[node.closest_lane_idx]),
                    (node.car.x, node.car.y))
        # print distance
        score -= distance*distance * 10

        # tangents = self.lane.sample_tangents()
        # print tangents 
        # print car.theta , tangents[node.closest_lane_idx]
        # diff = car.theta - tangents[node.closest_lane_idx]
        # diff -= np.round(diff / 360) * 360
        # print diff
        # score -= (diff*diff)
        # print tangents[node.closest_lane_idx] 

        # pri

        for othercar in self.cars:
            if othercar.id != node.car.id:
                dist = Utils.distance_between(
                            (othercar.x, othercar.y),
                            (node.car.x, node.car.y))
                if dist < (node.car.collision_radius() + othercar.collision_radius()):
                    score = -1e10

        # f = 0.0
        # score = f * np.array(node.heuristic_history).mean() + (1-f) * score

        return score
