#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool

from Utils import Utils
from CamView import CamView

import scipy.optimize as opt
import math

class Optimize(object):
    """docstring for Optimize"""
    def __init__(self,lane):
        self.lane = lane


    def gradients(self, distances, positions):
        indices = np.round(positions).astype("int32")

        lower_bound_x = indices[:,0]>=0
        lower_bound_y = indices[:,1]>=0
        upper_bound_x = indices[:,0]<distances.shape[0]-1
        upper_bound_y = indices[:,1]<distances.shape[1]-1
        lower_bounds = np.logical_and(lower_bound_x, lower_bound_y)
        upper_bounds = np.logical_and(upper_bound_x, upper_bound_y)
        in_bounds_x = np.logical_and(lower_bound_x,upper_bound_x)
        in_bounds_y = np.logical_and(lower_bound_y,upper_bound_y)
        in_bounds = np.logical_and(lower_bounds,upper_bounds)

        dx = distances[indices[in_bounds,0]+1,indices[in_bounds,1]] - distances[indices[in_bounds,0],indices[in_bounds,1]]
        dy = distances[indices[in_bounds,0],indices[in_bounds,1]+1] - distances[indices[in_bounds,0],indices[in_bounds,1]]
        # ds = positions - indices

        gradients = np.zeros_like(positions)
        gradients[in_bounds,0] = dx
        gradients[in_bounds,1] = dy

        # add borders
        # left = np.logical_and(np.logical_not(lower_bound_x),in_bounds_y)
        # right = np.logical_and(np.logical_not(upper_bound_x),in_bounds_y)
        # top = np.logical_and(np.logical_not(lower_bound_y),in_bounds_x)
        # bottom = np.logical_and(np.logical_not(upper_bound_y),in_bounds_x)

        gradients[np.logical_not(lower_bound_x),0] = 2
        gradients[np.logical_not(upper_bound_x),0] = -2
        gradients[np.logical_not(lower_bound_y),1] = 2
        gradients[np.logical_not(upper_bound_y),1] = -2

        # todo

        return gradients


    def optimize_correction_gradient(self, edge_points, distances, camview, x0, y0, theta0, skip = 1, maxiter=10, k=1):
        # correct for cam view flipped coordinates and offset
        if edge_points.shape[0] == 0:
            return (0,0,0),0
        # correct for cam view flipped coordinates and offset
        edge_points = camview.transform_camview_to_car_xy(edge_points)

        if skip > 0:
            edge_points = edge_points[::(skip+1),:]

        # transformed = np.array(Utils.rotate_points(edge_points,camview_angle_offset + theta0))
        # transformed += (x0,y0)
        # gradients = self.gradients(distances, transformed)

        # print gradients.mean(axis=0)

        # edge_points must be corrected for cam view flipped coordinates and offset, not for angle_offset!
        def error_function(param, edge_points, x0, y0, theta0, camview, distances, k=1):
            x, y, theta = param
            transformed = camview.transform_car_xy_to_global(edge_points,
                camview.angle_offset + theta0 + theta,
                x0+x,y0+y)
            indices = np.round(transformed).astype("int32")
            errors = np.zeros(shape=(transformed.shape[0]),dtype="float32")

            in_bounds = np.logical_and(
                np.logical_and(
                    indices[:,0]>=0,
                    indices[:,1]>=0),
                np.logical_and(
                    indices[:,0]<distances.shape[0]-1,
                    indices[:,1]<distances.shape[1]-1))

            # get distances for transformed points in bounds 
            errors[in_bounds] = distances[indices[in_bounds,0],indices[in_bounds,1]]

            # add subpixel interpolation
            dx = distances[indices[in_bounds,0]+1,indices[in_bounds,1]] - distances[indices[in_bounds,0],indices[in_bounds,1]]
            dy = distances[indices[in_bounds,0],indices[in_bounds,1]+1] - distances[indices[in_bounds,0],indices[in_bounds,1]]
            ds = transformed - indices
            errors[in_bounds] += dx * ds[in_bounds,0] + dy * ds[in_bounds,1]
            
            # only use errors for transformed points in bounds
            errors = errors[in_bounds]
            
            # apply power
            if k != 1:
                errors = np.power(errors, k)
            
            # mean of errors
            if errors.shape[0] > 0:
                error = errors.mean()
            else:
                error = 1e5

            # get closest point on lane
            closest_lane_idx = self.lane.closest_sampled_idx(x0+x, y0+y)

            # reward proximity to lane
            dist_lane = Utils.distance_between(
                        (self.lane.sampled_x[closest_lane_idx],self.lane.sampled_y[closest_lane_idx]),
                        (x0+x, y0+y))
            error += dist_lane*dist_lane * 20


            # regularisation
            error += 1 * (param**2).sum()

            # calculate xy gradients
            gradients = self.gradients(distances, transformed)

            # calculate torques
            torques = np.cross(transformed - [x0+x,y0+y],gradients,axis=1)

            # calculate parameter gradient
            mean_gradient = gradients.mean(axis=0) * 15
            mean_torque = -torques.mean() * 10.1
            param_gradient = np.array([mean_gradient[0],mean_gradient[1],mean_torque])

            # print x, y, theta, error 
            return error, param_gradient

        res = opt.minimize(error_function,(0,0,0),
            jac=True, # error_function returns gradient along with the error
            args=(edge_points, x0, y0, theta0, camview, distances, k),
            options={
                "maxiter":maxiter,
                "eps":1e-1
                }
            )
        # print transformed [:10]
        # print (transformed - [x0,y0])[:10]
        # print gradients[:10]
        # print np.cross((transformed - [x0,y0]),gradients)[:10]
        # print np.cross((transformed - [x0,y0]),gradients).shape
        # print np.array([[1,2], [4,5],[4,7],[3,9]])
        # print np.array([[4,5], [1,2],[3,9],[4,7]])
        # print np.cross(np.array([[1,2], [4,5],[4,7],[3,9]]),np.array([[4,5], [1,2],[3,9],[4,7]]))
        
        # torques = np.cross(transformed - [x0,y0],gradients,axis=1)
        # print torques.mean()

        # mean_gradient = gradients.mean(axis=0) * 5
        # mean_torque = torques.mean() * 0.1
        # resX = (mean_gradient[0],mean_gradient[1],mean_torque)
        # return resX, 1/0.1
        # return resX, (error_function(resX, edge_points, x0, y0, theta0, camview_angle_offset, distances, k) / 50)
        return res.x,res.fun


    def optimize_correction(self, edge_points, distances, camview, x0, y0, theta0, skip = 1, maxiter=10, k=1):
        if edge_points.shape[0] == 0:
            return (0,0,0),0
        # correct for cam view flipped coordinates and offset
        edge_points = camview.transform_camview_to_car_xy(edge_points)

        if skip > 0:
            edge_points = edge_points[::(skip+1),:]

        # edge_points must be corrected for cam view flipped coordinates and offset, not for angle_offset!
        def error_function(param, edge_points, x0, y0, theta0, camview, distances, k=1):
            x, y, theta = param
            transformed = camview.transform_car_xy_to_global(edge_points,
                camview.angle_offset + theta0 + theta,
                x0+x,y0+y)
            indices = np.round(transformed).astype("int32")
            errors = np.zeros(shape=(transformed.shape[0]),dtype="float32")

            in_bounds = np.logical_and(
                np.logical_and(
                    indices[:,0]>=0,
                    indices[:,1]>=0),
                np.logical_and(
                    indices[:,0]<distances.shape[0]-1,
                    indices[:,1]<distances.shape[1]-1))

            # get distances for transformed points in bounds 
            errors[in_bounds] = distances[indices[in_bounds,0],indices[in_bounds,1]]

            # add subpixel interpolation
            dx = distances[indices[in_bounds,0]+1,indices[in_bounds,1]] - distances[indices[in_bounds,0],indices[in_bounds,1]]
            dy = distances[indices[in_bounds,0],indices[in_bounds,1]+1] - distances[indices[in_bounds,0],indices[in_bounds,1]]
            ds = transformed - indices
            errors[in_bounds] += dx * ds[in_bounds,0] + dy * ds[in_bounds,1]
            
            # only use errors for transformed points in bounds
            errors = errors[in_bounds]
            
            if k != 1:
                errors = np.power(errors, k)
            
            if errors.shape[0] > 0:
                error = errors.mean()
            else:
                error = 1e5

            # print x, y, theta, error 
            return error

        res = opt.minimize(error_function,(0,0,0),
            args=(edge_points, x0, y0, theta0, camview, distances, k),
            options={
                "maxiter":maxiter,
                "eps":1e-1
                }
            )
        return res.x, res.fun

    def correct_xy_nearest_edge_single_pass(self, edge_points_in_car_xy, x0, y0, theta0, labels, label_positions, camview,skip=5):
        transformed = camview.transform_car_xy_to_global(edge_points_in_car_xy,
                angle = theta0 + camview.angle_offset,
                global_x = x0, 
                global_y = y0)

        xx,yy = transformed[:,0], transformed[:,1]
        # select points that in bound of labeled area
        in_bounds = np.logical_and(np.logical_and(xx>=0,yy>=0),np.logical_and(xx<labels.shape[0],yy<labels.shape[1]))

        # get nearest points according to labels and label_positions of all transformed points in bounds
        nearest_edge = np.array([label_positions[label] for label in labels[xx[in_bounds],yy[in_bounds]]])

        xcorr = (nearest_edge[:,0] - xx[in_bounds]).mean()
        ycorr = (nearest_edge[:,1] - yy[in_bounds]).mean()
        return (xcorr, ycorr)

    def distance_mean(self, xytheta, edge_points, x0, y0, theta0, camview, distances, k=1):
        if edge_points.shape[0] == 0:
            return None
        edge_points_in_car_xy = camview.transform_camview_to_car_xy(edge_points)
        return self.distance_mean_in_car_xy(xytheta, edge_points_in_car_xy, x0, y0, theta0, camview, distances, k)

    def distance_mean_in_car_xy(self, xytheta, edge_points_in_car_xy, x0, y0, theta0, camview, distances, k=1):
        if edge_points_in_car_xy.shape[0] == 0:
            return None
        x, y, theta = xytheta
        transformed = camview.transform_car_xy_to_global(edge_points_in_car_xy,
            camview.angle_offset + theta0 + theta,
            x0+x,y0+y)
        indices = np.round(transformed).astype("int32")
        errors = np.zeros(shape=(transformed.shape[0]),dtype="float32")

        in_bounds = np.logical_and(
            np.logical_and(
                indices[:,0]>=0,
                indices[:,1]>=0),
            np.logical_and(
                indices[:,0]<distances.shape[0]-1,
                indices[:,1]<distances.shape[1]-1))

        # get distances for transformed points in bounds 
        errors[in_bounds] = distances[indices[in_bounds,0],indices[in_bounds,1]]

        # add subpixel interpolation
        dx = distances[indices[in_bounds,0]+1,indices[in_bounds,1]] - distances[indices[in_bounds,0],indices[in_bounds,1]]
        dy = distances[indices[in_bounds,0],indices[in_bounds,1]+1] - distances[indices[in_bounds,0],indices[in_bounds,1]]
        ds = transformed - indices
        errors[in_bounds] += dx * ds[in_bounds,0] + dy * ds[in_bounds,1]
        
        # only use errors for transformed points in bounds
        errors = errors[in_bounds]
        
        if k != 1:
            errors = np.power(errors, k)
        
        if errors.shape[0] > 0:
            error = errors.mean()
        else:
            error = None

        # print x, y, theta, error 
        return error



    def correct_xy_nearest_edge_multi_pass(self, edge_points, x0, y0, theta0, labels, label_positions, camview, skip=5, tol=1e1, maxiter=10):
        if edge_points.shape[0] == 0:
            return (0,0)
        car_xy = camview.transform_camview_to_car_xy(edge_points)
        i = 0
        xcorr, ycorr = 0,0
        
        while True:
            transformed = camview.transform_car_xy_to_global(car_xy,
                    angle = theta0 + camview.angle_offset,
                    global_x = x0+xcorr, 
                    global_y = y0+ycorr)

            xx,yy = transformed[:,0], transformed[:,1]
            # select points that in bound of labeled area
            in_bounds = np.logical_and(np.logical_and(xx>=0,yy>=0),np.logical_and(xx<labels.shape[0],yy<labels.shape[1]))

            # get nearest points according to labels and label_positions of all transformed points in bounds
            nearest_edge = np.array([label_positions[label] for label in labels[xx[in_bounds],yy[in_bounds]]])

            if nearest_edge.shape[0] > 0:
                # print "nearest_edge.shape", nearest_edge.shape
                # print "xx.shape", xx.shape
                # print "in_bounds.shape", in_bounds.shape
                # print "xx[in_bounds].shape", xx[in_bounds].shape
                xcorr += (nearest_edge[:,0] - xx[in_bounds]).mean()
                ycorr += (nearest_edge[:,1] - yy[in_bounds]).mean()

            i += 1
            if (i >= maxiter) or (math.sqrt(xcorr*xcorr+ycorr*ycorr) < tol):
                break

        return (xcorr, ycorr)

    # returns list of lists of indices into points
    def cluster(self, points, hilbert, cutoff):
        idxs = np.arange(points.shape[0])
        # return [idxs] # stub! everything in one cluster
        
        # sort points according to its hilbert values
        sorted_idxs = sorted(idxs,key=lambda idx:hilbert[points[idx][0],points[idx][1]])

        
        ## create clusters from sorted list 
        # create new cluster when next point in sorted list if too far from points in current cluster
        clusters = []
        current = []
        for idx in sorted_idxs:
            if current == []:
                current.append(idx)
            else:
                # calculate distances from idx to all points in current
                dxs = points[current,0] - points[idx,0]
                dys = points[current,1] - points[idx,1]
                dists = np.sqrt(dxs*dxs+dys*dys)
                if dists.min() > cutoff:
                    # idx too far away from even the nearest point in current
                    # -> create new cluster
                    clusters.append(current)
                    current = [idx]
                else:
                    # otherwise add idx to current
                    current.append(idx)
                    

        # add last remaining cluster
        if len(current) > 0:
            clusters.append(current)

        return clusters


    def correct_theta_nearest_edge(self, edge_points, x0, y0, theta0, xcorr, ycorr, labels, label_positions, hilbert, camview, skip=5, cutoff=10):
        transformed = camview.transform_camview_to_car_xy(edge_points)
        transformed = camview.transform_car_xy_to_global(transformed,
                angle = theta0 + camview.angle_offset,
                global_x = x0+xcorr, 
                global_y = y0+ycorr)

        xx,yy = transformed[:,0], transformed[:,1]
        # select points that in bound of labeled area
        in_bounds = np.logical_and(np.logical_and(xx>=0,yy>=0),np.logical_and(xx<labels.shape[0],yy<labels.shape[1]))

        # get nearest points according to labels and label_positions of all transformed points in bounds
        nearest_edge = np.array([label_positions[label] for label in labels[xx[in_bounds],yy[in_bounds]]])

        # find clusters in nearest points on bg edge to transformed
        clustered_nearest = self.cluster(nearest_edge, hilbert, cutoff)

        # corrections
        thetacorrs = []

        # for each cluster: cluster corresponding transformed points creating subclusters
        for cluster in clustered_nearest:
            # get points of cluster
            cluster_nearest = nearest_edge[cluster]
            cluster_transformed = transformed[in_bounds][cluster]

            clustered_transformed = self.cluster(cluster_transformed, hilbert, cutoff)
            # (clustered_transformed points into cluster_transformed and cluster_nearest)

            # for each subcluster: 
            # orientation correction by subtraction of orientation of principal axis from 
            # subcluster transformed points and corresponding nearest_edge points
            for subcluster in clustered_transformed:
                if len(subcluster) >= 2: # we need at least 2 to get orientation info
                    subcluster_nearest = cluster_nearest[subcluster]
                    subcluster_transformed = cluster_transformed[subcluster]
                    orientation_nearest = Utils.orientation_of_points(subcluster_nearest)
                    orientation_transformed = Utils.orientation_of_points(subcluster_transformed)
                    thetacorrs.append(orientation_nearest - orientation_transformed)

        thetacorrs = np.array(thetacorrs) / Utils.d2r
        # mean of corrections
        return thetacorrs.mean()