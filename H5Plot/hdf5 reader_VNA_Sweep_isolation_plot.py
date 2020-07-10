# -*- coding: utf-8 -*-
"""
Created on Thu Mar 05 16:38:54 2020

@author: WangLab
"""

import os
import time
import lmfit 
import matplotlib
matplotlib.interactive(True)


import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from matplotlib import gridspec
filepath = r'C:\Users\WangLab\Documents\yingying\0612cooldown\\9mK_18_59_3'

timelist = np.loadtxt(filepath)

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '0827cooldown_circualtor_VNA - Copy.hdf5'
#hdf5_name = '0808cooldown_FMR - Copy (4).hdf5'
date = '20200310'
linewidth = []

#for time in ['135518','144555','153200','162022','165755','173609','181741','185126']:
#for time in ['122746','125127','131643','133959','140913','143530','150150']:
for time in ['121502']:
#for time in timelist[:]:
    time = str(int(time)).zfill(6)
#    experiment = 'Power_Sweep_VNA'
    experiment = 'Current_Sweep_VNA'
    fit_S12 = False
    fit_S11 = False
    
    subtract = False
    average = 1
    
    if subtract:
    #    hdf5_name_s = '0531cooldown_FMR.hdf5'
        hdf5_name_s = hdf5_name
        date_s = '20190903'
        time_s = '224029'
        experiment_s = 'SingleTrace'
    
    def S21(params, x, y):
        est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
        est = est * np.exp(1j*params['phi'])
        if np.max(np.abs(y)) < limit_for_off:
            est = est + params['roff'] + 1j*params['ioff']

        
        return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
        
        
    def S11(params, x, y):
    
        est = (-1 - params['kappa_1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2))*params['A']
        return y - abs(est)
    
    
    limit_for_off = 1
    
    ''' Primary x axis and secondary if 2d'''
    #x_key = 'freqs'
    #x2_key = 'powers'
    
    f = h5.File(filepath + hdf5_name, 'r')
    exp = f['/' + date + '/' + time + '_' + experiment]
    y_keys = exp.keys()
    #print(y_keys)
#    exp_ = f['/' + date + '/' + '123511' + '_' + experiment]
    #y_keys.remove(x_key)
    #y_keys.remove(x2_key)
    freq = exp['freqs'].value
    powers = exp['currents'].value
#    powers = exp['powers'].value
#    powers = exp['fields'].value
    real = exp['realS21'].value
    imag = exp['imaginaryS21'].value
    real2 = exp['realS12'].value
    imag2 = exp['imaginaryS12'].value
    f.close()

    '''Conversion factor from Yoko current in mA to actual magnetic field in mT'''
    #if current.any() < 0.5:
    #    field = current*529.37 + 0.49
    #else:
    #    field = -268.93 * (current)**2 + 839.69*current - 88.67
    
    '''Plot'''
    
    

    pl.figure()
    figname = ''
    powerplot = np.concatenate((powers, np.zeros(1) + powers[1]-powers[0] + powers[-1]))
    mag = 10*np.log10(real**2 + imag**2)
    mag2 = 10*np.log10(real2**2 + imag2**2)
    Z = np.transpose(mag - mag2)
    #X,Y = np.meshgrid(field, freq)
    X,Y = np.meshgrid(powerplot, freq)
#    pl.xlim(X.min(), X.max())
    pl.pcolormesh(X,Y/1e9,Z, vmax = 0, vmin = -40,cmap='RdBu')
    pl.colorbar()
#    
    pl.title('S12 isolation',fontsize = 14)
    pl.xlabel('Magnetic Field(T)',fontsize = 12)
    pl.ylabel('Frequency(GHz)',fontsize = 12)
    
#    fig = pl.figure()
#    gs = gridspec.GridSpec(1, 2)
#    fig.add_subplot(gs[0])
#    fig.add_subplot(gs[1])
    
    
    
    
        
    

