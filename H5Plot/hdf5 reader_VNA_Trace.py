# -*- coding: utf-8 -*-
"""
Created on Thu May 16 11:24:57 2019

@author: Wang_Lab
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
hdf5_name = '20190322 Cooldown.hdf5'
date = '20190422'
time = '170423'
experiment = 'SingleTraceNoAsync'

fit_S12 = True

fit_S11 = False




def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est * np.exp(1j*params['phi'])
    
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

#y_keys.remove(x_key)
#y_keys.remove(x2_key)
freq = exp['freqs'].value
#current = exp['currents'].value
real = exp['real'].value
imag = exp['imaginary'].value


mag = 10*np.log10(real**2 + imag**2)
fig = pl.figure()
gs = gridspec.GridSpec(1, 2)
fig.add_subplot(gs[0])
fig.add_subplot(gs[1])
fig.axes[1].plot(real[0],imag[0])
fig.axes[0].plot(freq[0]/1e9,mag[0])





freqs = freq[0]
datas = real[0] + 1j*imag[0]
if fit_S12:
    params = lmfit.Parameters()
    params.add('kappa_prod', value= (np.max(np.abs(datas))*0.5e6)**2.001, min = 0)#,vary = False)
    params.add('omega_c', value=freqs[np.argmax(np.abs(datas))]*1.0001,min = freqs[np.argmax(np.abs(datas))]*0.9998, max = freqs[np.argmax(np.abs(datas))] * 1.0002)#,vary = False)
    params.add('kappa_a', value=1e6, min = 0)#, max = 4e6)#,vary = False)
    if np.max(np.abs(datas)) < limit_for_off:
        params.add('roff',value = 1e-5)#,vary = False)
        params.add('ioff',value = 1e-5)#, vary = False)
    params.add('phi',value = -1, max = np.pi, min = -np.pi)#,vary = False)
            
#    datas = realdata[0,:]+ 1j*imagdata[0,:]    
    result = lmfit.minimize(S21, params, args=(freqs, datas))
    lmfit.report_fit(result.params)
    print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
    fitdata = np.sqrt(result.params['kappa_prod'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )
    if np.max(np.abs(datas)) < limit_for_off:
        fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
    fitdata = fitdata * np.exp(1j*result.params['phi'].value)
    fitdatadB = 20*np.log10(np.abs(fitdata))
#    ampdata = 20*np.log10(np.sqrt(realdata[0,:]**2 + imagdata[0,:]**2))
if fit_S11:
    params = lmfit.Parameters()
    params.add('kappa_1', value=2.1305e+05)
    params.add('omega_c', value=freqs[np.argmin(np.abs(datas))]*1.0001)
    params.add('kappa_a', value=3.0022e+06)
    params.add('A', value=1)
            
#    datas = realdata[0,:]+ 1j*imagdata[0,:]    
    result = lmfit.minimize(S11, params, args=(freqs, abs(datas)))
    lmfit.report_fit(result.params)
    print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
    print ('coupling Q: ',result.params['omega_c'].value/result.params['kappa_1'].value)
    fitdata = (-1 - result.params['kappa_1'].value / (-1j*(freqs-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value
    fitdatadB = 20*np.log10(np.abs(fitdata))


#    fig.axes[0].set_title(figname)
#    pl.suptitle(figname)
if fit_S12 or fit_S11:
    fig.axes[0].plot(freqs/float(1e9), fitdatadB,'--' )
    fig.axes[1].plot(fitdata.real,fitdata.imag, '--')

#    pl.xlabel('freq(GHz)')

fig.axes[1].set_aspect('equal', 'box')
    
pl.legend()