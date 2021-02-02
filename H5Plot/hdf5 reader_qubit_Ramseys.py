# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 23:34:36 2020

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
hdf5_name = '0915cooldown_circulator - Copy.hdf5'
date = '20201009'
#experiment = 'ROCavSpectroscopy_keysight'
#experiment = 'Power_Sweep_VNA'
f = h5.File(filepath + hdf5_name, 'r')
j = 0




field = 0.05
nrows = 3
repeat = 11
fix_phi0 = None
if j == 0:
    freqs = np.zeros([nrows,repeat])
    taus = np.zeros([nrows,repeat])
#    freq2 = np.zeros([nrows,repeat*2])
#
#if three_modes:
#    if j == 0:
#        freq1 = np.zeros([nrows,len(fields)])
#        freq2 = np.zeros([nrows,len(fields)])


for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if int(title[0:6]) <= int('090000') and int(title[0:6]) > int('015319') and title[7:13] == 'Ramsey':# and title[7:12] =='ROCav':
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

        seq_num = 2
        xs = delays
        ys = phase_data.value
        if np.max(ys) - np.min(ys)>300:# and meas.proj_func is 'phase':
    
            for iphase in range(len(ys)):
                if ys[iphase] > 0:
                    ys[iphase] = ys[iphase] -360  
        fig = pl.figure()
        fig.add_subplot(111)
        fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3, linestyle='-', markerfacecolor='red')
    
        amp0 = (np.max(ys) - np.min(ys)) / 2
        fftys = np.abs(np.fft.fft(ys - np.average(ys)))
        fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
        f0 = np.abs(fftfs[np.argmax(fftys)])
        print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)
    
        params = lmfit.Parameters()
        params.add('ofs', value=np.average(ys))
        params.add('amp', value=amp0, min=0.1)
        params.add('tau', value=xs[-1], min=1, max=2e5)
        params.add('freq', value=f0, min=0)
        if j ==0:
            params.add('slope', value=0,min = 0, vary = False)
            params.add('A', value = 0,  vary = False)
            params.add('A2', value = 0, vary = False) 
        else:
            
            params.add('slope', value=.005,min = 0, vary = False)
            params.add('A', value = -1e-3, max = 0, vary = True)
            params.add('A2', value = 2e-3, min = 0, vary = True)
    #    if meas.echotype == ECHO_NONE:
    #
    #        params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)  #Changed to plus sign for accommodate for amplitude RO, need a good LT solution
    #
    #    elif meas.echotype == ECHO_HAHN:
    #        params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi) #DARIO added to fit better for echo vs plain T2
    #Yingying changed phi0 to checking value of first point
        if  fix_phi0 is None:
            if ys[0] < np.average(ys):
                params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)
            else:
                params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True) #Yingying changed phi0 to checking value of first point
        else:
            params.add('phi0', value=fix_phi0, vary=False)
        result = lmfit.minimize(changing_freq_fit, params, args=(xs, ys))
    #    lmfit.report_fit(params)
    #    result2 = lmfit.minimize(t2_fit, result.params, args=(xs,ys))
        lmfit.report_fit(result.params)
    
        fig.axes[0].plot(xs/1e3, -changing_freq_fit(result.params, xs, 0), 
                label='Fit, tau=%.03f us, df=%.03f kHz, df_final = %.03f kHz,\n df_average = %.03f kHz\n tau_i = %.04f us, tau_f = %.04f us, tau_ave = %.04f us'%(
                        result.params['tau'].value/1000, 
                        result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[0]*result.params['slope']),
                        result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[-1]*result.params['slope']),
                        np.average(result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs*result.params['slope'])),
                        0.001/((1/result.params['tau'].value) + result.params['A2'].value*np.exp(-xs[0]*result.params['slope'].value/2)),
                        0.001/((1/result.params['tau'].value) + result.params['A2'].value*np.exp(-xs[-1]*result.params['slope'].value/2)),
                        0.001/np.average((1/result.params['tau'].value) + result.params['A2'].value*np.exp(-xs*result.params['slope'].value/2))                   
                        ))
        fig.axes[0].legend()
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Time [us]')
#        fig.axes[1].plot(xs/1e3, changing_freq_fit(result.params, xs, ys), marker='s')
        fig.canvas.draw()
        freqs[0][j] = result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[0]*result.params['slope'])
        freqs[1][j] = result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[-1]*result.params['slope'])
        freqs[2][j] = np.average(result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs*result.params['slope']))
        taus[0][j] = 0.001/((1/result.params['tau'].value) + result.params['A2'].value*np.exp(-xs[0]*result.params['slope'].value/2))
        taus[1][j] = 0.001/((1/result.params['tau'].value) + result.params['A2'].value*np.exp(-xs[-1]*result.params['slope'].value/2))
        taus[2][j] = 0.001/np.average((1/result.params['tau'].value) + result.params['A2'].value*np.exp(-xs*result.params['slope'].value/2))

        if j >0:            
            pl.close()
        j = j + 1
            
if repeat >1:
    pl.figure()
    pl.title('field = %s T'%(field))


    if repeat >1:
        pl.figure()
        pl.title('field = %s T'%(field))
        pl.plot(freqs[0,1:], label = ' df_initial, ave freq = %.3f +/- %.3f kHz'%(
                np.average(freqs[0,1:]), np.std(freqs[0,1:])/np.sqrt(len(freqs[0,1:]))))
        pl.plot(freqs[1,1:], label = ' df_final, ave freq = %.3f +/- %.3f kHz'%(
                np.average(freqs[1,1:]), np.std(freqs[1,1:])/np.sqrt(len(freqs[1,1:]))))
        pl.plot(freqs[2,1:], label = ' df_average, ave freq = %.3f +/- %.3f kHz'%(
                np.average(freqs[2,1:]), np.std(freqs[2,1:])/np.sqrt(len(freqs[2,1:]))))
        pl.plot(np.zeros(repeat -1) + freqs[2,0], label = ' df_average w/o cavity disp, ave freq = %.3f'%(
                freqs[2,0]))
        pl.legend()
        fn = os.path.join(r'C:\_Data', 'images/%s_qubit_df.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        pl.savefig(fn, **kwargs)
        pl.figure()
        pl.title('field = %s T'%(field))
        pl.plot(taus[0,1:], label = ' tau_initial, ave tau = %.3f +/- %.3f us'%(
                np.average(taus[0,1:]), np.std(taus[0,1:])/np.sqrt(len(taus[0,1:]))))
        pl.plot(taus[1,1:], label = ' tau_final, ave tau = %.3f +/- %.3f us'%(
                np.average(taus[1,1:]), np.std(taus[1,1:])/np.sqrt(len(taus[1,1:]))))
        pl.plot(taus[2,1:], label = ' tau_average, ave tau = %.3f +/- %.3f us'%(
                np.average(taus[2,1:]), np.std(taus[2,1:])/np.sqrt(len(taus[2,1:]))))
        pl.plot(np.zeros(repeat -1) + taus[2,0], label = ' tau_average w/o cavity disp, ave freq = %.3f'%(
                taus[2,0]))
        pl.legend()

