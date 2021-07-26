# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 11:40:50 2019

@author: Wang_Lab
"""

import os
import time
import glob
if 0:
    os.system(r'C:\qrlab-3\start.bat')
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
def S21_two_modes_V3(params, x, y):
    est = np.sqrt(params['kappa_prod1'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )* np.exp(1j*params['phi1'])
    est = est + np.sqrt(params['kappa_prod2'])/(-1j*(x-params['omega_c2'])-(params['kappa_a2'])/2.0 ) * np.exp(1j*(params['phi21']+params['phi1']))
    est = est * np.exp(1j* params['slope'] * x)
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
#    est = est * np.exp(1j* params['slope'] * x)   
   
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)

''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '0626cooldown_circualtor - Copy (2).hdf5'
date = '20200728'
time = '151744'
experiment = 'ROCavSpectroscopy_keysight_mixer_cw'

''' Primary x axis and secondary if 2d'''
x_key = 'freqs'
#x2_key = 'powers'

two_modes = True
one_mode = False

f = h5.File(filepath + hdf5_name, 'r')

expgroup = f['/' + date]

cut_freq = 0
pl.figure('fit')
#for i, filename in enumerate(expgroup.keys()[40:]):
#    
#    
exp = expgroup[time + '_' + experiment]
y_keys = list(exp.keys())

    
xs = exp[x_key].value
data = exp['amplitudes'].value
#data_c = exp['avg'].value
amp = exp['amplitudes'].value[0]
phase = exp['phases'].value[0]

datas = amp * np.exp(1j * phase *np.pi/180)
    
ys = data[0]
fig = pl.figure()
fig.add_subplot(111)
fig.axes[0].plot(xs/1e6,ys)
if one_mode:
        
    params = lmfit.Parameters()
    if cut_freq == 0:
        
        cut_freq = xs[-1]
        
        
    #    else:
    #        cut_freq = xs[int(np.where(xs ==int( freq1/2e5)*2e5)[0])+np.argmin(ys[int(np.where(xs ==int( freq1/2e5)*2e5)[0]):int( np.where(xs == int( freq2/2e5)*2e5)[0])])]
    
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
    print(('fit freq: %s +/- %s  '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6)))
    freq1 = result.params['freq'].value
    
    fig.axes[0].plot(xs1/1e6, -S21fit(result.params, xs1, 0), label='fit freq: %s +/- %s MHz '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
    fig.axes[0].legend()
    #    
    #    xs2 = xs[int((cut_freq-xs[0])/(xs[-1]- xs[0]) * len(xs)):len(xs)-1]
    #    ys2 = ys[int((cut_freq-xs[0])/(xs[-1] - xs[0]) * len(xs)):len(xs)-1]
    #        
    #    params.add('kappa_prod', value= 1e11,min = 0)
    #    params.add('freq', value=xs2[np.argmax(ys2)], max = xs2[np.argmax(ys2)] * 1.01, min = xs2[np.argmax(ys2)] * 0.99)
    #    
    #    params.add('kappa_a', value=1.5e6, min = 0)#, max = 4e6)#,vary = False)
    #    params.add('roff', value = np.min(ys2)/2)
    #    params.add('ioff', value = np.min(ys2)/2)
    #    
    #            
    #    #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
    #    result = lmfit.minimize(S21fit, params, args=(xs2,ys2))
    #    lmfit.report_fit(result.params)
    #    print ('fit freq: %s +/- %s  '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
    #    freq2 = result.params['freq'].value
    #    pl.figure('fit')
    #    pl.scatter(i,freq1)
    #    pl.scatter(i,freq2)
    #    
    #    fig.axes[0].plot(xs2/1e6, -S21fit(result.params, xs2, 0), label='fit freq: %s +/- %s MHz '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
    #    fig.axes[0].legend()
    
    
    #    
    #    fig.axes[0].plot(-xs/1e6, ys)
    fig.axes[0].set_xlabel('freqs (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()
    f.close()
    
if two_modes:

    limit_for_off = 20
    freqs = xs
    params = lmfit.Parameters()
    params.add('kappa_prod1', value= 1e13, min = 0)#,vary = False)
    params.add('omega_c', value=10.809e9)#,vary = False)
    params.add('kappa_a', value=2e6, min = 0)#,vary = False)
    if np.max(np.abs(datas)) < limit_for_off:
        params.add('roff',value =(datas[0].real+ datas[-1].real)/2)
        params.add('ioff',value = (datas[0].imag+ datas[-1].imag)/2)
    params.add('phi1',value = 1.15, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
            
    
    params.add('kappa_prod2', value= 1e13, min = 0)#,vary = False)
    params.add('omega_c2', value=10.81e9)#,vary = False)
    params.add('kappa_a2', value=2e6, min = 0)#,vary = False)
    params.add('phi21',value = 4.88, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
    params.add('slope', value = -4.7e-7)
    result = lmfit.minimize(S21_two_modes_V3, params, args=(freqs, datas))
    lmfit.report_fit(result.params)
    fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
    fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
    fitdata = fitdata1 + fitdata2
    fitdata = fitdata * np.exp(1j * result.params['slope']*freqs)
    if np.max(np.abs(datas)) < limit_for_off:
        fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
    #fitdata = fitdata * np.exp(1j * result.params['slope']*freqs)    
    

    phase_p = phase-freqs*result.params['slope']*180/np.pi
    datas_p = amp * np.exp(1j * phase_p *np.pi/180)
    fig = pl.figure()
    fig.add_subplot(131)
    fig.axes[0].plot(freqs/1e6,amp,label = '-6dB')
    fig.add_subplot(132)
    fig.add_subplot(133)
    fig.axes[2].plot(datas_p.real,datas_p.imag)  
    fig.axes[1].plot(freqs/float(1e6),phase_p%360)  
    fig.axes[0].plot(freqs/float(1e6), np.abs(fitdata),'--' )
    fig.axes[1].plot(freqs/float(1e6),(np.angle(fitdata, deg = True)-freqs*result.params['slope']*180/np.pi)%360, '--') 
    fitdata_p = np.abs(fitdata) * np.exp(1j * (np.angle(fitdata)-freqs*result.params['slope']))
    fig.axes[2].plot(fitdata_p.real,fitdata_p.imag, '--')
    pl.xlabel('freq(MHz)')

#    freq1[j%nrows][j/nrows] = result.params['omega_c'].value
#    freq1_err[j%nrows][j/nrows] = result.params['omega_c'].stderr
#    freq2[j%nrows][j/nrows] = result.params['omega_c2'].value      #np.average(ys)
#    freq2_err[j%nrows][j/nrows] =result.params['omega_c2'].stderr
#    j = j+1
#    fn = os.path.join(r'C:\Users\Wang_Lab\Documents\yingying\03172020cooldown', 'fitting\%s_%s.png'%(title,j-1))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    pl.savefig(fn, **kwargs)
    f.close()

    
    
    
    
    
    