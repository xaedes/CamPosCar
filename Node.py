#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Node(object):
	"""docstring for Node"""
	def __init__(self, car, action, prevNode = None):
		super(Node, self).__init__()
		self.car = car
		self.action = action
		self.prevNode = prevNode
		