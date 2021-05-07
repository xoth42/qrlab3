# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 14:27:04 2021

@author: WangLab
"""

import matplotlib
matplotlib.interactive(True)
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
hdf5_name = '20210105cooldown_circulator_VNA - Copy.hdf5'
#hdf5_name = '0612cooldown_FMR - Copy.hdf5'

date = '20210222'
#time = '182303'
experiment = 'SingleTrace'
#experiment = 'SingleTraceNoAsync'


''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
powers = np.linspace(-25,-10,2)
nfreqs = 1601
repeat = 20

count = 0

if count == 0:
    datas_power = np.zeros((len(powers),nfreqs),dtype = complex)
    datas_repeat = np.zeros((repeat,nfreqs),dtype = complex)
    fig = pl.figure('averaged trace')
    gs = gridspec.GridSpec(1, 2)
    fig.add_subplot(gs[0])
    fig.add_subplot(gs[1])
    fig = pl.figure()
    gs = gridspec.GridSpec(1, 2)
    fig.add_subplot(gs[0])
    fig.add_subplot(gs[1])
for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if title[7:13] == 'Single' and int(title[0:6]) <= int('094850') and int(title[0:6]) >int('041526'):
        print title
        
        exp = f[date][title]
        y_keys = exp.keys()
#        xs = exp['detunings'].value
#        data = exp['avg_pp'].value
#        data_c = exp['avg'].value
        

        #exp = f['/' + date + '/' + time + '_' + experiment]
        #y_keys = exp.keys()
        #print(y_keys)
        
        #y_keys.remove(x_key)
        #y_keys.remove(x2_key)
        freq = exp['freqs'].value
        
        real = exp['real'].value
        imag = exp['imaginary'].value
        
        
        
        
        datas = real + 1j*imag
        #datas = datas * np.exp(1j *15e-9 * freq)
        mag = np.abs(datas)
        mag = 20*np.log10(mag)
        
        

#        
#        
#        
        fig.axes[1].plot(real[0],imag[0])
        fig.axes[0].plot(freq[0]/1e9,mag[0])
        freqs = freq[0]
        datas = real + 1j*imag        
        datas_repeat[count%repeat] = datas  
        

        if count%repeat == (repeat - 1):
            datas_power[count/repeat] =datas_repeat.mean(axis = 0)
            fig = pl.figure('averaged trace')

            fig.axes[1].plot(datas_power[count/repeat].real,datas_power[count/repeat].imag)
            fig.axes[0].plot(freq[0]/1e9,20*np.log10(np.abs(datas_power[count/repeat])))
#            datas_repeat = np.zeros((repeat,nfreqs),dtype = complex)
            fig = pl.figure()
            gs = gridspec.GridSpec(1, 2)
            fig.add_subplot(gs[0])
            fig.add_subplot(gs[1])
            
        count +=1
        
f.close()        
        
        
        
