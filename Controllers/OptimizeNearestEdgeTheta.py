#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from Controller import Controller
from Utils import Utils

class OptimizeNearestEdgeTheta(Controller):
    """docstring for OptimizeNearestEdgeTheta"""
    def __init__(self, optimize, labels, label_positions, hilbert, camview, estimate_car, skip=5):
        super(OptimizeNearestEdgeTheta, self).__init__()
        self.optimize = optimize
        self.labels = labels
        self.label_positions = label_positions
        self.hilbert = hilbert
        self.camview = camview
        self.estimate_car = estimate_car
        self.skip = skip

    def update(self, car, dt):
        actual_view = self.camview.view
        if actual_view is not None:
            bw = actual_view[:,:,0]
            edge_points = Utils.zero_points(bw)[::self.skip,:]
            edge_points_in_car_xy = self.camview.transform_camview_to_car_xy(edge_points)

            # correct estimate 
            thetacorr = self.optimize.correct_theta_nearest_edge(
                edge_points,
                x0 = self.estimate_car.x,
                y0 = self.estimate_car.y,
                theta0 = self.estimate_car.theta,
                xcorr = 0,
                ycorr = 0,
                labels = self.labels,
                label_positions = self.label_positions, 
                hilbert = self.hilbert,
                camview = self.camview, 
                skip = self.skip)


            # set car to corrected estimate
            car.x = self.estimate_car.x
            car.y = self.estimate_car.y
            car.theta = self.estimate_car.theta + thetacorr

    def draw(self, screen, car):
        pass


