# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 10:25:10 2018

@author: wanglab
"""
import matplotlib
matplotlib.interactive(True)

import os
from mclient import instruments


VNA = instruments['VNA']

import matplotlib.pyplot as pl 

filename = '220\\V3'
print filename
newpath = r'C:\Users\wanglab\Documents\\yingying\\FMR\\0.25T in fridge\\%s.txt'%(filename)

if not os.path.exists(os.path.dirname(newpath)):

    os.makedirs(os.path.dirname(newpath))
pl.figure()
data = VNA.do_get_data()
axis = VNA.do_get_xaxis()

axis = axis / float(1000000000)
pl.xlabel('frequency(GHZ)')


pl.plot(axis, data[0], label = filename)

pl.ylabel('dB')
#pl.show()
pl.legend()

import numpy as np
axis = axis[:,None].T
trace = np.concatenate([axis,data]).T

np.savetxt(newpath , trace , delimiter=",") # saves data

