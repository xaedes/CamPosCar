#!/usr/bin/env python
# -*- coding: utf-8 -*-
from copy import copy

class Node(object):
	"""docstring for Node"""
	def __init__(self, car, action=None, prevNode = None):
		super(Node, self).__init__()
		self.car = car
		self.action = action
		self.prevNode = prevNode
		self.children = []
		if self.prevNode is not None:
			self.prevNode.children.append(self)


	def advance(self, action, timestep):
		return Node(
				car = copy(self.car).forward(action,timestep), 
				action = action, 
				prevNode = self)

