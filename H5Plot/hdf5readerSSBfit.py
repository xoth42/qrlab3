# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 11:40:50 2019

@author: Wang_Lab
"""
#
#import os
#import time
#if 0:
#    os.system(r'C:\qrlab\start.bat')
#    time.sleep(1)
#
#from pulseseq import sequencer, pulselib
##from scripts.single_qubit import rabi
#from scripts.single_cavity import WignerbyParity
    
#import mclient
#from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from lib.math import fit
import lmfit

def Gaussfit(params, x, y):
    est = params['Amp'] * np.exp(-(x-params['freq'])**2/(2 * params['kappa']**2)) + params['off']
    
    return y - est

''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '1122cooldown_Circulator_cavity - Copy (2).hdf5'
date = '20191210'
time = '153250'
experiment = 'SSBSpec_Gaussianfit'

''' Primary x axis and secondary if 2d'''
x_key = 'detunings'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = exp.keys()

    
xs = exp[x_key].value
data = exp['avg_pp'].value
data_c = exp['avg'].value


    
ys = data
fig = pl.figure()
fig.add_subplot(111)
fig.axes[0].plot(xs/1e6,ys)

params = lmfit.Parameters()


#    if np.max(ys) + np.min(ys) < 2 * np.average(ys):
if 0:
    params.add('Amp', value= -(np.max(ys)-np.min(ys)))
    params.add('freq', value=xs[np.argmin(ys)])
else:
    
    params.add('Amp', value= (np.max(ys)-np.min(ys)))
    params.add('freq', value=-1)#xs[np.argmax(ys)])

params.add('kappa', value=01e6, min = 0)#, max = 4e6)#,vary = False)
params.add('off', value = np.average(ys))

        
#    datas = realdata[0,:]+ 1j*imagdata[0,:]    
result = lmfit.minimize(Gaussfit, params, args=(xs,ys))
lmfit.report_fit(result.params)
print ('fit freq: %s +/- %s  '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))


fig.axes[0].plot(xs/1e6, -Gaussfit(result.params, xs, 0), label='fit freq: %s +/- %s MHz '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
fig.axes[0].legend()



#    
#    fig.axes[0].plot(-xs/1e6, ys)
fig.axes[0].set_xlabel('Detuning (MHz)')
fig.axes[0].set_ylabel('Intensity (AU)')
fig.canvas.draw()
f.close()