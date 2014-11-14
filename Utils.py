#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Utils(object):

	@classmethod
	def inRect(CLS, rect, i, j):
	    x,y,w,h = rect
	    return i >= x and i <= x + w - 1 and  j >= y and j <= y + h - 1
