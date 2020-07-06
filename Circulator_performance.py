# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 13:09:23 2019

@author: WangLab
"""

import matplotlib
matplotlib.interactive(True)
import h5py as h5
import numpy as np
import matplotlib.pyplot as pl

filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '0808cooldown_FMR - Copy (5).hdf5'
#hdf5_name = '0612cooldown_FMR - Copy.hdf5'
date = '20190819'
time1 = '152615'
time2 = '152814'

#experiment = 'SingleTrace'
experiment = 'SingleTraceNoAsync'
f = h5.File(filepath + hdf5_name, 'r')
exp1 = f['/' + date + '/' + time1 + '_' + experiment]
freq1 = exp1['freqs'].value
real1 = exp1['real'].value
imag1 = exp1['imaginary'].value
mag1 = (real1**2 + imag1**2)**.5

exp2 = f['/' + date + '/' + time2 + '_' + experiment]
freq2 = exp2['freqs'].value
real2 = exp2['real'].value
imag2 = exp2['imaginary'].value
mag2 = (real2**2 + imag2**2)**.5

performance = mag1/mag2
pl.figure()
pl.title('Commercial Circulator Performance between Ports 1 and 2')
pl.plot(freq1[0],performance[0])
pl.ylabel('S21/S12')
pl.xlabel('frequency GHz')
pl.show()
