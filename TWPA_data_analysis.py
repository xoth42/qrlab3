# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 15:09:59 2019

@author: WangLab
"""

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import lmfit
from lmfit import Parameters, Minimizer, report_fit
#C:\_Data\MultiCavity_0726Cooldown - Copy (2).hdf5
#'c:/_data/MultiCavity_0726Cooldown - Copy.hdf5'
filepath = r'C:\_Data\\'
hdf5_name = r'MultiCavity_0726Cooldown - Copy (2).hdf5'
date1 = '20190728'
f = h5.File(filepath + hdf5_name, 'r')
background = '/20190728/152424_SingleTraceNoAsync' #data file of high power sweep for background to do background subtraction
background_freq = f[background]['freqs'].value
background_real = f[background]['real'].value
background_imag = f[background]['imaginary'].value
background_mag = (background_real**2 + background_imag**2)**.5
exp1 = f['/' + date1]
trials1 = []
for name in exp1: #creating a list of all files containing desired data
    trials1.append(name)
initial = (trials1.index('144310_Power_Sweep_VNA'))
trials1 = trials1[initial:len(trials1)-1]
date1_add = [date1]*len(trials1)
trials1 = ['/' + date1_add[i] + '/' + trials1[i] for i in range(len(trials1))]
#for i in range(trials1):
exp = f[str(trials1[1])]
freq = exp['freqs'].value
real = exp['realS21'].value
imag = exp['imaginaryS21'].value
powers = exp['powers'].value
mag = (real**2 + imag**2)**.5
print(freq)
