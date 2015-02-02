#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen

from Controller import Controller
from Utils import Utils

class OptimizeNearestEdgeXYSinglePass(Controller):
    """docstring for OptimizeNearestEdgeXYSinglePass"""
    def __init__(self, optimize, labels, label_positions, camview, estimate_car, skip=5):
        super(OptimizeNearestEdgeXYSinglePass, self).__init__()
        self.optimize = optimize
        self.labels = labels
        self.label_positions = label_positions
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
            xcorr,ycorr = self.optimize.correct_xy_nearest_edge_single_pass(
                edge_points_in_car_xy, 
                x0 = self.estimate_car.x, 
                y0 = self.estimate_car.y, 
                theta0 = self.estimate_car.theta, 
                labels =  self.labels, 
                label_positions =  self.label_positions, 
                camview =  self.camview, 
                skip = self.skip)

            # set car to corrected estimate
            car.x = self.estimate_car.x + xcorr
            car.y = self.estimate_car.y + ycorr
            car.theta = self.estimate_car.theta

    def draw(self, screen, car):
        pass


