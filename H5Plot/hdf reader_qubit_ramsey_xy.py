# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 14:57:24 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 22:15:28 2020

@author: Wang_Lab
"""


import os
import time
import glob


import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
#import json
#from lib.math import fit
import lmfit

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
    exp = np.exp(-(x*((1 / params['tau'].value) + params['A2'].value*np.exp(-x*params['slope'].value/2))))
    est = params['ofs'].value + params['amp'].value * exp * sine
#    print params
    return data - est


''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '11262020cooldown_circulator - Copy (2).hdf5'
date = '20201210'
#experiment = 'ROCavSpectroscopy_keysight'
#experiment = 'Power_Sweep_VNA'
f = h5.File(filepath + hdf5_name, 'r')
j = 0



CW_qubit = False
field = 0
nrows = 2
repeat = 4
fix_phi0 = None
if j == 0:
    freqs = np.zeros([nrows,repeat])
    taus = np.zeros([nrows,repeat])
#
#if three_modes:
#    if j == 0:
#        freq1 = np.zeros([nrows,len(fields)])
#        freq2 = np.zeros([nrows,len(fields)])
exp_t = 'Ramsey_Measurement_mixer_xy'

for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if int(title[0:6]) <= int('182728') and int(title[0:6]) > int('182032') and title[7:] == exp_t:# and title[7:12] =='ROCav':
        print title



        x_key = 'delays'
        #x2_key = 'powers'
        exp = f[date][title]
        y_keys = exp.keys()
        
            
        delays = exp[x_key].value
#        amp = exp['amplitudes'].value[0]
#        phase = exp['phases'].value[0]
#        
##        freqs = freqs[40:100]
##        amp = amp[40:100]
##        phase = phase[40:100]
#        datas = amp * np.exp(1j * phase *np.pi/180)
        
        
        comp_data = exp['avg']
        phase_data = exp['avg_pp']
        
        pl.figure('complex plane')
        pl.scatter(np.real(comp_data),np.imag(comp_data), label = '%s'%(i))
        p = np.polyfit(np.real(comp_data), np.imag(comp_data), 1)
        pl.plot(np.linspace(np.min(np.real(comp_data)), np.max(np.real(comp_data)), 11), 
                p[0] * np.linspace(np.min(np.real(comp_data)), np.max(np.real(comp_data)), 11) + p[1])
        
        vec = np.array([1,p[0]])/np.sqrt(1 + p[0]**2)
        data_o = comp_data - np.average(comp_data)
        data_vec = np.vstack((np.real(data_o),np.imag(data_o)))
        proj = np.matmul(vec, data_vec)

#        center = np.mean(comp_data)
#        v_1 = comp_data[np.argmax()]
        seq_num = 2
        xs = delays
        ys_als = np.zeros([seq_num , len(xs)])
#        ys_als[0] = phase_data.value[0::seq_num]
#        ys_als[1] = phase_data.value[1::seq_num]
        ys_als[0] = proj[0::seq_num]
        ys_als[1] = proj[1::seq_num]

        fig = pl.figure()
        fig.add_subplot(111)
#        gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
        fig.axes[0].scatter(xs/1e3, ys_als[0])
        fig.axes[0].scatter(xs/1e3, ys_als[1])
        fig.axes[0].plot(xs/1e3, np.sqrt(ys_als[0]**2 + ys_als[1]**2))

#        fig.add_subplot(132)
#        fig.axes[1].plot(freqs/1e6,phase)
        
        params = lmfit.Parameters()
        
        
        if np.max(ys_als) - np.min(ys_als)>300:# and meas.proj_func is 'phase':
    
            for iphase in range(len(ys_als)):
                if ys_als[iphase] > 0:
                    ys_als[iphase] = ys_als[iphase] -360  

        
        labels = ['sigma_x','sigma_y']
        off = np.zeros(seq_num)
        n_scale = np.zeros(seq_num)
        for l in range(seq_num):
            ys = ys_als[l]
            
            amp0 = (np.max(ys) - np.min(ys)) / 2
            fftys = np.abs(np.fft.fft(ys - np.average(ys)))
            fftfs = np.fft.fftfreq(len(ys), np.abs(xs[1]-xs[0]))
            f0 = np.abs(fftfs[np.argmax(fftys)])
            print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)
        
            params = lmfit.Parameters()
            params.add('ofs', value=np.average(ys))
            params.add('amp', value=amp0, min=0.1)
            params.add('tau', value=max(xs)*0.7, min=1, max=2e5)
            params.add('freq', value=f0, min=0)
            params.add('slope', value = 0.005)#value=0,vary = False)
            params.add('A', value = -0.001)#value = 0, vary = False)
            params.add('A2', value = 0.001)#value = 0, vary = False)
        #    if meas.echotype == ECHO_NONE:
        #
        #        params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)  #Changed to plus sign for accommodate for amplitude RO, need a good LT solution
        #
        #    elif meas.echotype == ECHO_HAHN:
        #        params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi) #DARIO added to fit better for echo vs plain T2
            if  fix_phi0 is None:
                if ys[0] < np.average(ys):
                    params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)
                else:
                    params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True) #Yingying changed phi0 to checking value of first point
            else:
                params.add('phi0', value=fix_phi0, vary=False)
    #        else:
    #            params.add('phi0',value = return_result[0]['phi0'].value, vary = False)
            result = lmfit.minimize(changing_freq_fit, params, args=(xs, ys))
        #    lmfit.report_fit(params)
        #    result2 = lmfit.minimize(t2_fit, result.params, args=(xs,ys))
            lmfit.report_fit(result.params)
            freqs[l][j] = result.params['freq'].value
            taus[l][j] = result.params['tau'].value
#            return_result.append(result.params)
#            if meas.double_freq == False:
            fig.axes[0].plot(xs/1e3, -changing_freq_fit(result.params, xs, 0), 
                    label='Fit, tau=%.03f us, df=%.03f kHz, %s'%(
                            result.params['tau'].value/1000,
                            result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[0]*result.params['slope']),
#                            result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[-1]*result.params['slope'])))
                            labels[l]))
            fig.axes[0].legend()
            fig.axes[0].set_ylabel('Intensity [AU]')
            fig.axes[0].set_xlabel('Time [us]')
#            fig.axes[1].plot(xs/1e3, changing_freq_fit(result.params, xs, ys), marker='s')
            fig.canvas.draw()
            
            off[l] = result.params['ofs'].value 
            n_scale[l] = result.params['amp'].value
        offset = np.average(off)
        norm_scale = np.average(n_scale)
        
        pl.figure()
        pl.title('envelope graph')
        pl.plot(xs/1e3, np.sqrt((ys_als[0]-offset)**2 + (ys_als[1]-offset)**2)/norm_scale)
        pl.plot(xs/1e3, (ys_als[0]-offset)/norm_scale, label = 'sigma x')
        pl.plot(xs/1e3, (ys_als[1]-offset)/norm_scale, label = 'sigma y')
        
        angle_data = np.arctan((ys_als[1]-offset)/(ys_als[0]-offset))
        
        for i in range(len(angle_data)-1):
            if angle_data[i+1] < (angle_data[i]-.75*np.pi/2):
                angle_data[i+1:] = angle_data[i+1:] + np.pi
        pl.figure()
        pl.title('accumulated phase')
        pl.plot(xs/1e3, angle_data)
#        if j >0:            
#            pl.close()
        j = j + 1
            
if repeat >1:

    pl.figure()
    pl.title('field = %s T'%(field))
    labels = ['sigma_x','sigma_y']
    freq = freqs
    for l in range(seq_num ):
        pl.plot(freq[l]*1000, label = labels[l] + ' ave freq = %.3f +/- %.3f MHz'%(
                np.average(freq[l]*1000), np.std(freq[l])/np.sqrt(len(freq[l]))*1000))

    pl.legend()  
    pl.figure()
    pl.title('field = %s T'%(field))
    labels = ['sigma_x','sigma_y']
    freq = freqs
    for l in range(seq_num ):
        pl.plot(taus[l]*1000, label = labels[l] + '  ave tau = %.3f +/- %.3f MHz'%(
                np.average(taus[l]*1000), np.std(taus[l])/np.sqrt(len(taus[l]))*1000))

    pl.legend()


