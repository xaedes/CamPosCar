#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import \
    division  # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np  # Numpy, das Number One Number Crunching Tool
import math

from Utils import Utils

class Heuristic(object):
    """docstring for Heuristic"""

    def __init__(self, lane):
        super(Heuristic, self).__init__()
        self.lane = lane
        self.traveled = None

    def evaluate(self, node):
        score = 0
        node.closest_lane_idx = self.lane.closest_sampled_idx(node.car.x, node.car.y)

        # reward travaling along the lane in a certain direction
        if node.prevNode is not None:
            diff = node.closest_lane_idx - node.prevNode.closest_lane_idx
            diff -= np.round(diff / self.lane.path_len) * self.lane.path_len
            score += diff * -100 

        # reward smooth actions
        score -= 50 * np.array(node.action_history).std()


        # reward proximity to lane
        distance = Utils.distance_between(
                    (self.lane.sampled_x[node.closest_lane_idx],self.lane.sampled_y[node.closest_lane_idx]),
                    (node.car.x, node.car.y))
        score -= distance*distance * 10

        # avoid collisions with other cars
        for other_car in node.other_cars:
            dist = Utils.distance_between(
                        (other_car.x, other_car.y),
                        (node.car.x, node.car.y))
            if dist < (node.car.collision_radius() + other_car.collision_radius()):
                score = -1e10 + dist*dist




        # f = 0.0
        # score = f * np.array(node.heuristic_history).mean() + (1-f) * score

        return score
