#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import matplotlib.pyplot as plt

class Plot(object):
    __fig_number__ = 0
    """Wrapper for dynamic (interactive) matplotlib plotting

    Usage:
    plt = Plot()
    arr = np.random.normal(0,1,100).cumsum()
    while true:
        plt.begin()
        arr = arr[1] + np.random.normal(0,1,100).cumsum()
        plt.fig.plot(arr)
        plt.end()
    """
    def __init__(self, auto_show = True):
        self.fig = plt
        self.fig_number = Plot.__fig_number__
        Plot.__fig_number__ += 1
        self.fig.figure(self.fig_number,figsize=(4,3))
        self.fig.ion() # enable interactive mode
        if auto_show:
            self.show()

    def show(self):
        self.fig.show()

    def begin(self):
        self.fig.figure(self.fig_number)
        self.fig.cla()
    
    def end(self):
        self.fig.draw()

class PlotCached(Plot):
    """docstring for PlotCached"""
    def __init__(self, auto_show = True):
        super(PlotCached, self).__init__(auto_show)
        self.cache = dict()
    def begin(self):
        self.fig.figure(self.fig_number)
    def plot(self, name, x, y = None, color = None):
        # this practicly makes x the optional argument instead of y
        if y is None:
            y,x = x,y


        if name not in self.cache:
            args = filter((lambda a: a is not None),[x,y,color])
            self.cache[name], = self.fig.plot(*args)
        else:
            if x is not None:
                self.cache[name].set_xdata(x)
            if y is not None:
                self.fig.ylim(y.min(),y.max())
                self.cache[name].set_ydata(y)
            if color is not None:
                self.cache[name].set_color(color)


class RingBufferPlot(PlotCached):
    """docstring for RingBufferPlot"""
    def __init__(self, ring_buffer, colors = ['r','b','g'], x_axis_channel = None, auto_show = True):
        super(RingBufferPlot, self).__init__(auto_show)
        self.ring_buffer = ring_buffer
        self.x_axis_channel = x_axis_channel
        self.n_y_channels = (self.ring_buffer.channels+(0 if x_axis_channel is None else 1))
        if type(colors) == list:
            self.colors = colors
        else:
            # allows to specify the color for each channel the same 
            self.colors = [self.colors] * self.n_y_channels

    def draw(self):
        self.begin()

        if self.x_axis_channel is not None:
            x_axis = self.ring_buffer.buffer[:,self.x_axis_channel]
        else:
            x_axis = np.arange(self.ring_buffer.length)

        for k, channel in enumerate(filter((lambda ch: ch != self.x_axis_channel), range(self.ring_buffer.channels))):
            self.plot(channel,x_axis,self.ring_buffer.buffer[:,channel],self.colors[k % len(self.colors)])

        self.end()

class HistogramPlot(Plot):
    """docstring for RingBufferPlot"""
    def __init__(self, bins, color = 'r', auto_show = True):
        super(HistogramPlot, self).__init__(auto_show)
        self.bins = bins
        self.color = color

    def draw(self, data):
        self.begin()
        self.fig.hist(data,self.bins)
        self.end()
        