#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np                 # Numpy, das Number One Number Crunching Tool

class RingBuffer(object):
    """docstring for RingBuffer"""
    def __init__(self, length, channels = 1):
        super(RingBuffer, self).__init__()
        self.length = length
        self.channels = channels
        self.buffer = np.zeros(shape=(self.length, self.channels))

    def add(self, data):
        self.buffer = np.roll(self.buffer, -1)
        self.buffer[-1,:] = data