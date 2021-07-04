# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 15:14:59 2019

@author: Wang_Lab
"""

import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as pl

wp = 10.8
wn = 10.6 + 1j*1
delta = 1
wp_p = []
wn_p = []
deltalist = np.linspace(0,1,101)
for delta in deltalist:
    H = np.array([[wp, delta],
              [delta, wn]])



    e,v =LA.eig(H)
#    print e
#    print v
    wp_p.append(e[0])
    wn_p.append(e[1])
print(e)
print(v)
pl.figure()
pl.subplot(211)   
pl.plot(deltalist,np.real(wp_p),label = 'real')
pl.plot(deltalist,np.real(wn_p))
pl.legend()
pl.subplot(212) 
pl.plot(deltalist,np.imag(wp_p),label = 'imag')
pl.plot(deltalist,np.imag(wn_p))
pl.legend()
    