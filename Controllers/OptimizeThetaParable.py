#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from Controller import Controller
from Utils import Utils

class OptimizeThetaParable(Controller):
    """docstring for OptimizeThetaParable"""
    def __init__(self, optimize, distances, camview, estimate_car, skip=5):
        super(OptimizeThetaParable, self).__init__()
        self.optimize = optimize
        self.distances = distances
        self.camview = camview
        self.estimate_car = estimate_car
        self.skip = skip

    def update(self, car, dt):
        actual_view = self.camview.view
        if actual_view is not None:
            bw = actual_view[:,:,0]
            edge_points = Utils.zero_points(bw)[::self.skip,:]

            # correct estimate 
            thetacorr = self.optimize.correct_theta_parable(
                edge_points = edge_points,
                x = self.estimate_car.x,
                y = self.estimate_car.y,
                theta0 = self.estimate_car.theta,
                camview = self.camview, 
                distances = self.distances
                )

            # set car to corrected estimate
            car.x = self.estimate_car.x
            car.y = self.estimate_car.y
            car.theta = self.estimate_car.theta + thetacorr

    def draw(self, screen, car):
        pass


