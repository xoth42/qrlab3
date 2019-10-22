# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 16:36:23 2019

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as pl
from matplotlib import gridspec
kp1 = 8.5e9
kp2 = 1.5e9
w1 = 10.9312e9
w2 = 10.935e9
k1 = 4e6
k2 = 1.8e6

fig = pl.figure()
gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
fig.add_subplot(gs[0])
fig.add_subplot(gs[1])

for phi in np.linspace(0,2*np.pi,11):

    
    x = np.linspace(10.9e9, 10.98e9, 1001)
    S21 = np.sqrt(kp1)/(1j*(x-w1)+k1) + np.exp(1j*phi)*np.sqrt(kp2)/(1j*(x-w2)+k2)
    S21_1 = np.sqrt(kp1)/(1j*(x-w1)+k1)
    S21_2 = np.exp(1j*phi)*np.sqrt(kp2)/(1j*(x-w2)+k2)
    
    
    fig.axes[0].plot(x, 20*np.log10(np.abs(S21)))
#    fig.axes[0].plot(x, 20*np.log10(np.abs(S21_1)))
#    fig.axes[0].plot(x, 20*np.log10(np.abs(S21_2)))
    
    #fig.axes[0].plot(x, np.abs(S21))
    #fig.axes[0].plot(x, np.abs(S21_1))
    #fig.axes[0].plot(x, np.abs(S21_2))
    
    fig.axes[1].plot(np.real(S21),np.imag(S21))
#    fig.axes[1].plot(np.real(S21_1),np.imag(S21_1))
#    fig.axes[1].plot(np.real(S21_2),np.imag(S21_2))
    fig.axes[1].set_aspect('equal', 'box')
    pl.show()