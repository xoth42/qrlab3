# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 10:41:05 2020

@author: Wang_Lab
"""

import os
import time
import lmfit 



import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import json
from matplotlib import gridspec
import scipy.linalg as la

wa = 10.8056
wb = 10.81103
wp = 10.7365
wn = 10.808
ga = .02967
ga2 = .007776
gb = ga
gb2 = ga2
spl = -.07673
A = 2.74
k = 8
gamma1 = 1e-5
gamma2 = 1e-5
gamma4 = .203

delta = np.linspace(0,.05,26)
input_port = 1
output_port = 3
gamma_list = [gamma1,gamma2,0,gamma4]
identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,0,0],[0,0,0,gamma4]])
out_3 = []
freqs = np.linspace(10.8,10.84,1601)
model_data_abs = np.zeros([26,1601])
model_data_phase = np.zeros([26,1601])
input_vec = np.matmul((-1j*identity*np.sqrt(gamma)),(identity[input_port].reshape(4,1)))
for i in range(len(delta)):
    H = np.array([[wa,0,ga,ga2],
                  [0,wb,-gb,gb2],
                  [ga,-gb,wp,1j*delta[i]*k+spl],
                  [ga2,gb2,-1j*delta[i]*k+spl, wn]])  
    H = H - 1j*gamma/2
    for j in range(len(freqs)):
        G = la.inv(freqs[j]*identity-H)
        cav_ops = np.matmul(G,input_vec)
        output = cav_ops[output_port][0]*gamma_list[output_port]
        model_data_abs[i][j] = abs(output)
        model_data_phase[i][j] = np.angle(output)
model_data_abs = model_data_abs*A

plt.figure()
plt.plot(freqs,model_data_abs[25])
        

    