# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 15:51:21 2020

@author: Wang_Lab
"""

import os
import time
import glob
if 0:
    os.system(r'C:\qrlab-3\start.bat')
    time.sleep(1)

#from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
#from scripts.single_cavity import WignerbyParity
    
#import mclient
#from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
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
hdf5_name = '0626cooldown_circualtor - Copy.hdf5'
date = '20200708'
time2 = '152557'
time1 = '153533'
experiment = 'ROCavSpectroscopy_keysight_mixer'
f = h5.File(filepath + hdf5_name, 'r')

x_key = 'freqs'
#x2_key = 'powers'
exp1 = f['/' + date + '/' + time1 + '_' + experiment]
exp2 = f['/' + date + '/' + time2 + '_' + experiment]


    
freqs = exp1[x_key].value
amp1 = exp1['amplitudes'].value[0]
phase1 = exp1['phases'].value[0]

amp2 = exp2['amplitudes'].value[0]
phase2 = exp2['phases'].value[0]

plt.figure()
plt.title('Amp subtraction')
plt.plot(freqs,amp2-amp1)

plt.figure()
plt.title('Phase subtration')
plt.plot(freqs,phase2-phase1)















