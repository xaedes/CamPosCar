#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool
import matplotlib.pyplot as plt

class Plot(object):
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
        self.fig.figure(0)
        self.fig.ion() # enable interactive mode
        if auto_show:
        	self.show()

    def show(self):
        self.fig.show()

    def begin(self):
    	self.fig.cla()
    
    def end(self):
    	self.fig.draw()