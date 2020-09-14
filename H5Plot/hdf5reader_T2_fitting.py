# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 15:16:44 2020

@author: Wang_Lab
"""

import os
import time
if 0:
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

#from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
from scripts.single_cavity import WignerbyParity
    
import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from matplotlib import gridspec
import lmfit


''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '0626cooldown_circualtor - Copy.hdf5'
date = '20200818'
time = '132735'
#experiment = 'Photon_Ramsey_Measurement_mixer'
experiment = 'Ramsey_Measurement_mixer'
''' Primary x axis and secondary if 2d'''
x_key = 'delays'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
#y_keys = exp.keys()
#print(y_keys)
x_data = exp[x_key].value[:71]

#y_keys.remove(x_key)
y_data = exp['avg_pp'].value[:71]

#def create_figure(self):

fig = pl.figure()
#title = self.title
#if self.data:
#    title += ' data in %s' % self.data.get_fullname()
#self.fig.suptitle(title)
#if not self.residuals:
#    self.fig.add_subplot(111)
#    return self.fig

#if self.res_vert:
gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
#else:
#    gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
fig.add_subplot(gs[0])
fig.add_subplot(gs[1])


def changing_freq_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-(c + f*exp(-s*x)) * x) * sin((d + g*exp(-s*x))* x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * (params['freq'].value + params['A']*np.exp(-params['slope'].value * x) ) + params['phi0'].value)
    exp = np.exp(-(x*(1 / params['tau'].value + params['A2']*np.exp(-x*params['slope']))))
    est = params['ofs'].value + params['amp'].value * exp * sine
    return data - est

def changing_freq_fit_T1exponential_overlay(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-(c + f*exp(-s*x)) * x) * sin((d + g*exp(-s*x))* x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * (params['freq'].value + params['A']*np.exp(-params['slope'].value * x) ) + params['phi0'].value)
    exp = np.exp(-(x*(1 / params['tau'].value + params['A2']*np.exp(-x*params['slope']))))
    est = params['ofs'].value + params['amp'].value * exp * sine
    est = est -params['A3']*np.exp(-x/params['T1'])
    return data - est

def asymmetric_oscillation_cavity_T2(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-(c + f*exp(-s*x)) * x) * sin((d + g*exp(-s*x))* x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''
    
    sine = np.sin(2 * np.pi * x * (params['freq'].value + params['A']*np.exp(-params['slope'].value * x) ) + params['phi0'].value)
    exp = np.exp(-(x*(1 / params['tau'].value + params['A2']*np.exp(-x*params['slope']))))
    est = np.zeros(len(sine))
    for i in range(len(sine)):
        if sine[i] < 0:
           est[i] = params['ofs'].value + params['amp_low'].value * exp[i] * sine[i] 
        else:
           est[i] = params['ofs'].value + params['amp_high'].value * exp[i] * sine[i]
    return data - est

with_T1 = False
asymetric_T2 = False
chang_freq = True 

xs = x_data
ys = y_data
#ys, fig = meas.get_ys_fig(data, fig)

if np.max(ys) - np.min(ys)>300:# and meas.proj_func is 'phase':

    for iphase in range(len(ys)):
        if ys[iphase] > 0:
            ys[iphase] = ys[iphase] -360   

fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3, linestyle='-', markerfacecolor='red')

amp0 = (np.max(ys) - np.min(ys)) / 2
amp_high = np.max(ys) - np.average(ys[-11:-1])
amp_low = -np.min(ys) + np.average(ys[-11:-1])
fftys = np.abs(np.fft.fft(ys - np.average(ys)))
fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
f0 = np.abs(fftfs[np.argmax(fftys)])
print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)

params = lmfit.Parameters()
params.add('ofs', value=np.average(ys))
params.add('tau', value=xs[-1], min=30, max=2e5)
params.add('freq', value=f0, min=.00001)
params.add('slope', value=0.005,vary =True)
params.add('A', value = 0, min = -5e-3, max = 0, vary = True)
params.add('A2', value = 0, vary = True)
if chang_freq:
    params.add('amp', value=amp0, min=0.1)
if with_T1:    
    params.add('A3', value = 7, vary = False)
    params.add('T1', value = 9.6e3, vary = False)
    params.add('amp', value=amp0, min=0.1)
if asymetric_T2:
    params.add('amp_low', value=amp_low, min=.55)
    params.add('amp_high', value=amp_high, min=0)
#    if meas.echotype == ECHO_NONE:
#
#        params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)  #Changed to plus sign for accommodate for amplitude RO, need a good LT solution
#
#    elif meas.echotype == ECHO_HAHN:
#        params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi) #DARIO added to fit better for echo vs plain T2
if ys[0] < np.average(ys):
    params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)
else:
    params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True) #Yingying changed phi0 to checking value of first point
if with_T1:
    result = lmfit.minimize(changing_freq_fit_T1exponential_overlay, params, args=(xs, ys))
if chang_freq:
    result = lmfit.minimize(changing_freq_fit, params, args=(xs, ys))
if asymetric_T2:
    result = lmfit.minimize(asymmetric_oscillation_cavity_T2, params, args=(xs, ys))
#    lmfit.report_fit(params)
#    result2 = lmfit.minimize(t2_fit, result.params, args=(xs,ys))
lmfit.report_fit(result.params)

if with_T1:
    fig.axes[0].plot(xs/1e3, -changing_freq_fit_T1exponential_overlay(result.params, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz, df_final = %.03f kHz'%(result.params['tau'].value/1000, result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[0]*result.params['slope']),result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[-1]*result.params['slope'])))
    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')
    fig.axes[1].plot(xs/1e3, changing_freq_fit_T1exponential_overlay(result.params, xs, ys), marker='s')
    fig.canvas.draw()
if chang_freq:
    fig.axes[0].plot(xs/1e3, -changing_freq_fit(result.params, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz, df_final = %.03f kHz'%(result.params['tau'].value/1000, result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[0]*result.params['slope']),result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[-1]*result.params['slope'])))
    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')
    fig.axes[1].plot(xs/1e3, changing_freq_fit(result.params, xs, ys), marker='s')
    fig.canvas.draw()
if asymetric_T2:
    fig.axes[0].plot(xs/1e3, -asymmetric_oscillation_cavity_T2(result.params, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz, df_final = %.03f kHz'%(result.params['tau'].value/1000, result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[0]*result.params['slope']),result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[-1]*result.params['slope'])))
    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')
    fig.axes[1].plot(xs/1e3, asymmetric_oscillation_cavity_T2(result.params, xs, ys), marker='s')
    fig.canvas.draw()
f.close()


##y_keys.remove(x2_key)
#
#
#qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
##qubit2_info = mclient.get_qubit_info('qubit2tone')
#
##cavity_infoR = mclient.get_qubit_info('cavity1R')
##cavity_infoA = mclient.get_qubit_info('cavityAlice')
#cavity_infoB = mclient.get_qubit_info('cavityBob')
#
##toload = ['qubit1ge', 'readout']
##mclient.load_settings_from_file(filepath + 'settings/' + date + '/' + time + '.set', toload)    # Last time-Rabi callibration
#
##qubits = mclient.get_qubits()
##qubit_info = mclient.get_qubit_info('qubit1ge')
#    
#tr = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB, t_ge=300, t_gf=0,
#                                         amax=1.75, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                                         seq=None, delay=5, saveas=None, bgcor=False)
#tr.displacements = exp[x_key].value
#data = exp['avg_pp'].value
##data = exp['avg_pp'].value[::2] - exp['avg_pp'].value[1::2]
##data /= 80
#tr.avg_data = exp['avg']
#tr.analyze(data = data)
#
#    
#pl.show()

