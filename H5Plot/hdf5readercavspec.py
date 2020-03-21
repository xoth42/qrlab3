# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 11:40:50 2019

@author: Wang_Lab
"""

import os
import time
import glob
if 0:
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
from scripts.single_cavity import WignerbyParity
    
import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from lib.math import fit
import lmfit

def S21fit(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['freq'])-(params['kappa_a'])/2.0 )
    est = est + params['roff'] + 1j*params['ioff']

    
    return y - np.abs(est)

''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '1122cooldown_Circulator_cavity - Copy (2).hdf5'
date = '20200103'
time = '001254'
experiment = 'ROCavSpectroscopy_keysight'

''' Primary x axis and secondary if 2d'''
x_key = 'freqs'
#x2_key = 'powers'



f = h5.File(filepath + hdf5_name, 'r')

expgroup = f['/' + date]

cut_freq = 0
pl.figure('fit')
for i, filename in enumerate(expgroup.keys()[40:]):
    
    
    exp = expgroup[filename]
    y_keys = exp.keys()
    
        
    xs = exp[x_key].value
    data = exp['amplitudes'].value
    #data_c = exp['avg'].value
    
    
        
    ys = data[0]
    fig = pl.figure()
    fig.add_subplot(111)
    fig.axes[0].plot(xs/1e6,ys)
    
    params = lmfit.Parameters()
    if cut_freq is 0:
        
        cut_freq = 10.713e9
        
        
    else:
        cut_freq = xs[int(np.where(xs ==int( freq1/2e5)*2e5)[0])+np.argmin(ys[int(np.where(xs ==int( freq1/2e5)*2e5)[0]):int( np.where(xs == int( freq2/2e5)*2e5)[0])])]
    
    xs1 = xs[0:int((cut_freq-xs[0])/(xs[-1]- xs[0]) * len(xs))]
    ys1 = ys[0:int((cut_freq-xs[0])/(xs[-1] - xs[0]) * len(xs))]
        
    params.add('kappa_prod', value= 1e12,min = 0)
    params.add('freq', value=xs1[np.argmax(ys1)], max = xs1[np.argmax(ys1)] * 1.01, min = xs1[np.argmax(ys1)] * 0.99)
    
    params.add('kappa_a', value=1.4e6, min = 0)#, max = 4e6)#,vary = False)
    params.add('roff', value = np.min(ys1)/2)
    params.add('ioff', value = np.min(ys1)/2)
    
            
    #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
    result = lmfit.minimize(S21fit, params, args=(xs1,ys1))
    lmfit.report_fit(result.params)
    print ('fit freq: %s +/- %s  '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
    freq1 = result.params['freq'].value
    
    fig.axes[0].plot(xs1/1e6, -S21fit(result.params, xs1, 0), label='fit freq: %s +/- %s MHz '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
    fig.axes[0].legend()
    
    xs2 = xs[int((cut_freq-xs[0])/(xs[-1]- xs[0]) * len(xs)):len(xs)-1]
    ys2 = ys[int((cut_freq-xs[0])/(xs[-1] - xs[0]) * len(xs)):len(xs)-1]
        
    params.add('kappa_prod', value= 1e11,min = 0)
    params.add('freq', value=xs2[np.argmax(ys2)], max = xs2[np.argmax(ys2)] * 1.01, min = xs2[np.argmax(ys2)] * 0.99)
    
    params.add('kappa_a', value=1.5e6, min = 0)#, max = 4e6)#,vary = False)
    params.add('roff', value = np.min(ys2)/2)
    params.add('ioff', value = np.min(ys2)/2)
    
            
    #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
    result = lmfit.minimize(S21fit, params, args=(xs2,ys2))
    lmfit.report_fit(result.params)
    print ('fit freq: %s +/- %s  '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
    freq2 = result.params['freq'].value
    pl.figure('fit')
    pl.scatter(i,freq1)
    pl.scatter(i,freq2)
    
    fig.axes[0].plot(xs2/1e6, -S21fit(result.params, xs2, 0), label='fit freq: %s +/- %s MHz '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
    fig.axes[0].legend()
    
    
    #    
    #    fig.axes[0].plot(-xs/1e6, ys)
    fig.axes[0].set_xlabel('freqs (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()
f.close()