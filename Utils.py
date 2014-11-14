#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division    # Standardmäßig float division - Ganzzahldivision kann man explizit mit '//' durchführen
import numpy as np

import math

class Utils(object):

    @classmethod
    def inRect(CLS, rect, i, j):
        x,y,w,h = rect
        return i >= x and i <= x + w - 1 and  j >= y and j <= y + h - 1

    @classmethod
    def distance_between(CLS, a, b):
        return math.sqrt(np.sum(np.square(np.array(a)-np.array(b))))