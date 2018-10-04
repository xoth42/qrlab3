# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 17:03:22 2018

@author: wanglab

Analyzing small asymmetry of the SSB spectra
"""

import numpy as np
from matplotlib import pyplot as plt

avgdata=spec.avg_data
n=len(avgdata)
original = np.array(avgdata)
plt.figure()

for ofs in [-2, -1, 0, 1, 2]:
#ofs = 0
    diff=[]
    for i in range(2, len(original)-3):
        diff.append(original[i]-original[n-1+ofs-i])
    plt.plot(diff)