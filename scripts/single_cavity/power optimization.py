# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:20:37 2019

@author: Wang_Lab
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import os
import time
import math
from scipy import optimize

np.random.seed(0)

x_data = np.linspace(-5,5, num=50)
y_data = 2.9* np.sin(1.5 * x_data) + np.random.normal(size=50)

plt.figure(figsize=(6,4))
plt.scatter(x_data, y_data)

def test_func(x,a,b):
    return a * np.sin(b*x)

params, params_covariance = optimize.curve_fit(test_func, x_data, y_data, p0 = [2,2])

print(params)

plt.figure(figsize=(6,4))
plt.scatter(x_data, y_data, label='Data')
plt.plot(x_data, test_func(x_data, params[0], params[1]))

#plt.legend(loc='best')
plt.show()