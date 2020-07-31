# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 11:17:39 2020

@author: Wang_Lab
"""


import os
import time
import lmfit 



import h5py as h5
import numpy as np
import matplotlib.pyplot as plt



def phase_chi(params, w, chi):
    lorentzian1 = 1/(params['kappa1']/2-1j*(w-params['w1']))
    lorentzian2 = 1/(params['kappa2']/2-1j*(w-params['w2']))
    theory_diff = (np.angle(lorentzian1)-np.angle(lorentzian2))*360/(2*np.pi) + params['offset']
    return chi - theory_diff
    #np.abs(y) - np.abs(est)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)


''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '1122cooldown_Circulator_cavity - Copy (3).hdf5'
date = '20200624'
experiment = 'Rabi_mixer'
f = h5.File(filepath + hdf5_name, 'r')

center_freq = 10.83e9
span = 10e6
freqs = np.linspace(center_freq-span,center_freq+span, 41)
fields = np.linspace(0,0.05,26)
nrows = 3

chis = []
for i, title in enumerate(f[date].keys()):

    if int(title[0:6]) <= int('154824') and int(title[0:6]) > int('152723') and title[7:17] =='Rabi_mixer':

        x_key = 'amps'
        #x2_key = 'powers'
        exp = f[date][title]
        y_keys = 'avg_pp'
        
            
        amps = exp[x_key].value
        phase = exp[y_keys].value
        chi = (phase[0]+phase[1])/2-phase[-1]
        chis.append(chi)

chis = chis[::-1][0:27]
freqs = freqs[0:27]
params = lmfit.Parameters()
params.add('kappa1', value= 1e6, min = 1e3, max = 8e7)#,vary = False)
params.add('kappa2', value= 1e6, min = 1e3, max = 8e7)#,vary = False)
params.add('w1', value = 10.825e9 , min = 10.82e9, max = 10.828e9)#,vary = False)
params.add('w2', value = 10.825e9 , min = 10.82e9, max = 10.828e9)
params.add('offset', value = 0, min = -180)

        
result = lmfit.minimize(phase_chi, params, args=(freqs, chis))
lmfit.report_fit(result.params)

lorentzian1 = np.sqrt(result.params['kappa1'].value)/(result.params['kappa1'].value/2-1j*(freqs-result.params['w1'].value))
lorentzian2 = np.sqrt(result.params['kappa2'].value)/(result.params['kappa2'].value/2-1j*(freqs-result.params['w2'].value))
theory_diff = (np.angle(lorentzian1)-np.angle(lorentzian2))*360/(2*np.pi) + result.params['offset'].value

plt.figure()
plt.title('fitting phase chi at .0T')
plt.xlabel('frequency')
plt.ylabel('chi')
plt.plot(freqs,chis[::-1], label = 'data')
plt.plot(freqs,theory_diff, label = "model")
plt.legend()