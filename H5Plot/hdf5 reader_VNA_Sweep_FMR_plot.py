# -*- coding: utf-8 -*-
"""
Created on Mon May 20 11:54:00 2019

@author: WangLab
"""
import os
import time
import lmfit 



import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from matplotlib import gridspec

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
#hdf5_name = 'FMR_RT_0515.hdf5'
hdf5_name = '0531Cooldown_FMR.hdf5'
date = '20190618'
time = '121301'
experiment = 'Current_Sweep_VNA'

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'currents'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = exp.keys()
#print(y_keys)

#y_keys.remove(x_key)
#y_keys.remove(x2_key)
freq = exp['freqs'].value
#field = exp['fields'].value
currents = exp['currents'].value
real = exp['realS21'].value
imag = exp['imaginaryS21'].value

'''Conversion factor from Yoko current in mA to actual magnetic field in mT'''
#if current.any() < 0.5:
#    field = current*529.37 + 0.49
#else:
#    field = -268.93 * (current)**2 + 839.69*current - 88.67

'''Plot'''
pl.figure()
figname = ''
#field = field * 1000
#field = np.zeros(len(currents))
field = currents
#for i in range(len(currents)):
#    if currents[i] < 0.5:
#        field[i] = 530.731*currents[i]
#    else:
#        field[i] = -257.872 *currents[i]**2 + 819.989 * currents[i] -80.161


mag = 10*np.log10(real**2 + imag**2)
Z = np.transpose(mag)
#X,Y = np.meshgrid(field, freq)
X,Y = np.meshgrid(field, freq/1e9)
pl.xlim(X.min(), X.max())
pl.ylim(Y.min(), Y.max())
pl.pcolormesh(X,Y,Z)
pl.colorbar()
#pl.title('YIG FMR Spectrum, S11 Measurement')
pl.xlabel('Magnetic Field(mT)')
pl.ylabel('Frequency(GHz)')
if 0:
    x = field
    Ms = 178 *1.15
    k = 1.008
    off = 0.63
    pl.plot(x, k*28.025*x/1000+off, color = 'b') #110
    pl.plot(x, k*28.025*(x+Ms*(0.4-0.333333))/1000+off, color = 'r') #220
    pl.plot(x, k*28.025*(x+Ms*(0.428571-0.333333))/1000+off, color = 'r') #330
    pl.plot(x, k*28.025*(x+Ms*(0.444444-0.333333))/1000+off, color = 'r') #440
    pl.plot(x, k*28.025*(x+Ms*(0.454545-0.333333))/1000+off, color = 'r') #550
    pl.plot(x, k*28.025*(x+Ms*(0.285714-0.333333))/1000+off, color = 'r') #320
    pl.plot(x, k*28.025*(x+Ms*(0.2-0.333333))/1000+off, color = 'r') #210
    pl.show()


if 0: # fitting seperate modes

    def S21(params, x, y):
            est = np.sqrt(params['kappa_prod'])/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
            est = est + params['roff'] + 1j*params['ioff']
            est = est * np.exp(1j*params['phi'])
#            est = est*(1-params['Asym']*(x-params['omega_c'])/(params['kappa_a']/2.0) )
            
#            return np.abs(y)-np.abs(est)
            return np.sqrt((y.real-est.real)**2 +(y.imag-est.imag)**2)