# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 16:27:07 2018

@author: Wang_Lab
"""
import numpy as np
import matplotlib.pyplot as pl

p = 0.003
i =1

d =1
t0 = 0.09
cool = 0.00002
t = []
t[0:20] = np.zeros(20) + 0.03
e = []
e[0:20] = np.zeros(20)
for j in range(500)[19:]:
    e.append( t0 - t[j])
    op = p*(e[j] + i * np.sum(e[j-20:j]) - d * (t[j]-t[j-1]))
    t.append(t[j]+op-cool)
#pl.figure()   
pl.plot(t)
#pl.plot(np.zeros(len(t)) + t0)