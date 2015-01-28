#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

class Kalman(object):
    """docstring for Kalman"""
    # http://www.cbcity.de/das-kalman-filter-einfach-erklaert-teil-2
    # http://de.wikipedia.org/wiki/Kalman-Filter
    def __init__(self, n_states, n_sensors):
        super(Kalman, self).__init__()
        self.n_states = n_states
        self.n_sensors = n_sensors

        # x: Systemzustand
        self.x = np.matrix(np.zeros(shape=(n_states,1)))

        # P: Unsicherheit ueber Systemzustand
        self.P = np.matrix(np.identity(n_states)) 

        # F: Dynamik
        self.F = np.matrix(np.identity(n_states))

        # Q: Dynamik Unsicherheit
        self.Q = np.matrix(np.identity(n_states))

        # u: externe Beeinflussung des Systems
        self.u = np.matrix(np.zeros(shape=(n_states,1)))

        # B: Dynamik der externen Einfluesse
        self.B = np.matrix(np.identity(n_states))

        # H: Messmatrix
        self.H = np.matrix(np.zeros(shape=(n_sensors, n_states)))

        # R: Messunsicherheit
        self.R = np.matrix(np.identity(n_sensors))

        # I: Einheitsmatrix
        self.I = np.matrix(np.identity(n_states))

        self.first = True

    def reset(self):
        self.x *= 0

    def update(self, Z):
        '''Z: new sensor values as numpy matrix'''

        # print 'Z.shape', Z.shape
        # print 'self.H.shape', self.H.shape
        # print 'self.x.shape', self.x.shape

        # w: Innovation
        w = Z - self.H * self.x
        #http://services.eng.uts.edu.au/~sdhuang/1D%20Kalman%20Filter_Shoudong.pdf 
        # gibt noch einen zusaetzlichen 'zero-mean Gaussian observation noise' v an, der drauf addiert wird (in gleichung (2))
        # in Gleichung (7) wird es jedoch nicht mit angegeben
        #http://services.eng.uts.edu.au/~sdhuang/Extended%20Kalman%20Filter_Shoudong.pdf
        # Gleichung(7)
        # beim EKF wird es zu w=Z-h(x)
        # h: observation function

        # S: Residualkovarianz (http://de.wikipedia.org/wiki/Kalman-Filter#Korrektur)
        S = self.H * self.P * self.H.getT() + self.R        # sieht in wikipedia etwas anders aus..
        #http://services.eng.uts.edu.au/~sdhuang/Extended%20Kalman%20Filter_Shoudong.pdf
        # Gleichung(9)
        # beim EKF wird es zu S=J_h*P*J_h^T + R
        # J_h:Jacobian of function h evaluated at next x, i.e. x after this update -> calculate x before S.

        # K: Kalman-Gain
        K = self.P * self.H.getT() * S.getI()
        #http://services.eng.uts.edu.au/~sdhuang/Extended%20Kalman%20Filter_Shoudong.pdf
        # Gleichung(10)
        # beim EKF wird es zu K=P*J_h^T * S^(-1)
        # J_h:Jacobian of function h evaluated at next x, i.e. x after this update -> calculate x before S.

        # x: Systemzustand
        self.x = self.x + K * w

        # P: Unsicherheit der Dynamik
        self.P = (self.I - K * self.H) * self.P
        # self.P = self.P - K * S * K.getT()
        #http://services.eng.uts.edu.au/~sdhuang/1D%20Kalman%20Filter_Shoudong.pdf 
        # ist in Gleichung (8) anders angegeben, vlt ist das aequivalent??

    def predict(self):
        # x: Systemzustand
        self.x = self.F * self.x + self.B * self.u  
        #http://services.eng.uts.edu.au/~sdhuang/1D%20Kalman%20Filter_Shoudong.pdf 
        # gibt noch einen zusaetzlichen 'zero-mean Gaussian process noise' w an, der drauf addiert wird (in Gleichung (1))
        # in Gleichung (5) wird es jedoch nicht mit angegeben, vlt ist w in G und u integriert?
        #http://services.eng.uts.edu.au/~sdhuang/Extended%20Kalman%20Filter_Shoudong.pdf
        # Gleichung(5)
        # beim EKF wird es zu x=f(x,u)

        # P: Unsicherheit der Dynamik
        self.P = self.F * self.P * self.F.getT() + self.Q   
        #http://services.eng.uts.edu.au/~sdhuang/Extended%20Kalman%20Filter_Shoudong.pdf
        # Gleichung(6)
        # beim EKF wird es zu P=J_f*P*J_f^T+Q
        # J_f:Jacobian of function f with respect to x evaluated at current x.
