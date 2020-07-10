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

#from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
#from scripts.single_cavity import WignerbyParity
    
#import mclient
#from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
#import json
#from lib.math import fit
import lmfit


limit_for_off = 20
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
hdf5_name = '1122cooldown_Circulator_cavity - Copy (2).hdf5'
date = '20200127'
#time = '150144'
#time = '150627'#gg
time = '151110' #eg
#time = '152228' #ge


experiment = 'ROCavSpectroscopy_keysight'




''' Primary x axis and secondary if 2d'''
x_key = 'freqs'
#x2_key = 'powers'
f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = exp.keys()

    
freqs = exp[x_key].value
amp = exp['amplitudes'].value[0]
phase = exp['phases'].value[0]

datas = amp * np.exp(1j * phase *np.pi/180)
    
#fig = pl.figure()
fig.add_subplot(131)
fig.axes[0].plot(freqs/1e6,amp)
fig.add_subplot(132)
#fig.axes[1].plot(freqs/1e6,phase)
params = lmfit.Parameters()


#f = h5.File(filepath + hdf5_name, 'r')
#
#expgroup = f['/' + date]

#cut_freq = None


    
params = lmfit.Parameters()
params.add('kappa_prod1', value= 4e13, min = 0)#,vary = False)
params.add('omega_c', value=10.711e9)#,vary = False)
params.add('kappa_a', value=1.5e6, min = 0)#,vary = False)
if np.max(np.abs(datas)) < limit_for_off:
    params.add('roff',value =(datas[0].real+ datas[-1].real)/2)
    params.add('ioff',value = (datas[0].imag+ datas[-1].imag)/2)
params.add('phi1',value = 1.2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
        

params.add('kappa_prod2', value= 1e13, min = 0)#,vary = False)
params.add('omega_c2', value=10.717e9)#,vary = False)
params.add('kappa_a2', value=1.5e6, min = 0)#,vary = False)
params.add('phi21',value = 0, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
params.add('slope', value = -4.8e-7)#,vary = False)
result = lmfit.minimize(S21_two_modes_V3, params, args=(freqs, datas))
#lmfit.report_fit(result.params)
fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
fitdata = fitdata1 + fitdata2
fitdata = fitdata * np.exp(1j * result.params['slope']*freqs)
if np.max(np.abs(datas)) < limit_for_off:
    fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
#fitdata = fitdata * np.exp(1j * result.params['slope']*freqs)    


phase_p = phase-freqs*result.params['slope']*180/np.pi
datas_p = amp * np.exp(1j * phase_p *np.pi/180)
fig.add_subplot(133)
fig.axes[2].plot(datas_p.real,datas_p.imag)  
fig.axes[1].plot(freqs/float(1e6),phase_p%360)  
fig.axes[0].plot(freqs/float(1e6), np.abs(fitdata),'--' )
fig.axes[1].plot(freqs/float(1e6),(np.angle(fitdata, deg = True)-freqs*result.params['slope']*180/np.pi)%360, '--') 
fitdata_p = np.abs(fitdata) * np.exp(1j * (np.angle(fitdata)-freqs*result.params['slope']))
fig.axes[2].plot(fitdata_p.real,fitdata_p.imag, '--')
pl.xlabel('freq(MHz)')

#fig.axes[1].set_aspect('equal', 'box')
f.close()

print 'freq1',result.params['omega_c'].value
print 'freq2',result.params['omega_c2'].value

#
#freqs = np.linspace(10e9, 11e9,1001)
#fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
#fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
#fitdata = fitdata1 + fitdata2
##fitdata = fitdata * np.exp(1j * result.params['slope']*freqs)
#if np.max(np.abs(datas)) < limit_for_off:
#    fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
#pl.figure()
#pl.plot(freqs, np.angle(fitdata))