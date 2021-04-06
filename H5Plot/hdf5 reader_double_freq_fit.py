# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 13:17:36 2021

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
import datetime
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
def t2_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-c * x) * sin(d * x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    exp = np.exp(-(x / params['tau'].value))
    est = params['ofs'].value + params['amp'].value * exp * sine
    return data - est

def double_sin_fit(params, x, data):
    '''
    Double exponentially decaying sine
    fit function: of + a1 * exp(-tau1 * x) * sin(f1 * x + phi1) + a2 * exp(-tau2 * x) * cos(f2 * x + phi2)
    '''
    exp1 = np.exp(-(x / params['tau'].value))
    exp2 = np.exp(-(x / params['tau'].value))#exp2 = np.exp(-(x / params['tau2'].value))  #Chen changed to single tau for both frequencies 8/24/19
    sin1 = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    sin2 = np.sin(2 * np.pi * x * params['freq2'].value + params['phi2'].value)
    est = params['ofs'].value + params['amp'].value * exp1 * sin1 + params['amp2'].value * exp2 * sin2
    return data - est

''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '01052021cooldown_circulator - Copy.hdf5'
date = '20210306'
#experiment = 'ROCavSpectroscopy_keysight'
#experiment = 'Power_Sweep_VNA'
f = h5.File(filepath + hdf5_name, 'r')
j = 0


save_data = False
CW_qubit = False
field = 0.015
nrows = 3
repeat = 20
fix_phi0 = None
proj = 'projection'
if j == 0:
    freqs = np.zeros([nrows,repeat])
    taus = np.zeros([nrows,repeat])
#
#if three_modes:
#    if j == 0:
#        freq1 = np.zeros([nrows,len(fields)])
#        freq2 = np.zeros([nrows,len(fields)])
if CW_qubit:
    exp_t = 'CW_Ram'
else:
    exp_t = 'Photon'

for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if int(title[0:6]) <= int('015018') and int(title[0:6]) > int('000644') and title[7:13] == exp_t:# and title[7:12] =='ROCav':
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
        ys_als = np.zeros([seq_num + 1, len(xs)])
        ys_als[0] = phase_data.value[0::seq_num]
        ys_als[1] = phase_data.value[1::seq_num]
        ys_cplx = comp_data.value   ####################
        if proj == 'phase':
            ys_als[2] = np.angle((ys_cplx[0::seq_num] + ys_cplx[1::seq_num])/2)*180/np.pi
        elif proj == 'amplitude':
            ys_als[2] = np.abs((ys_cplx[0::seq_num] + ys_cplx[1::seq_num])/2)
        elif proj == 'projection':

    
            ys = ((ys_cplx[0::seq_num] + ys_cplx[1::seq_num])/2)

            p = np.polyfit(np.real(ys), np.imag(ys), 1)
            vproj = 1 + 1j*p[0]

            vproj /= np.abs(vproj)
            ys_als[2] = np.real(ys) * vproj.real  + np.imag(ys) * vproj.imag
        fig = pl.figure()
        fig.add_subplot(111)
#        gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
        fig.axes[0].scatter(xs/1e3, ys_als[0])
        fig.axes[0].scatter(xs/1e3, ys_als[1])
        fig.axes[0].scatter(xs/1e3, ys_als[2])
#        fig.add_subplot(132)
#        fig.axes[1].plot(freqs/1e6,phase)
        
        params = lmfit.Parameters()
        
        
        if np.max(ys_als) - np.min(ys_als)>300:# and meas.proj_func is 'phase':
    
            for i in range(len(ys_als)):
                for iphase in range(len(ys_als[0])):
                    if ys_als[i][iphase] > 0:
                        ys_als[i][iphase] = ys_als[i][iphase] -360  
#        fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3, linestyle='-', markerfacecolor='red')
    
#        amp0 = (np.max(ys) - np.min(ys)) / 2
#        fftys = np.abs(np.fft.fft(ys - np.average(ys)))
#        fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
#        f0 = np.abs(fftfs[np.argmax(fftys)])
#        print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)
    
#        params = lmfit.Parameters()
#        params.add('ofs', value=np.average(ys))
#        params.add('amp', value=amp0, min=0.1)
#        params.add('tau', value=xs[-1], min=1, max=2e5)
#        params.add('freq', value=f0, min=0)
#        if meas.SS_mixer_info1.pi_amp ==0:
#            params.add('slope', value=0,min = 0, vary = False)
#            params.add('A', value = 0,  vary = False)
#            params.add('A2', value = 0, vary = False) 
#        else:
#            
#            params.add('slope', value=.01,min = 0, vary = True)
#            params.add('A', value = -1e-3, max = 0, vary = True)
#            params.add('A2', value = 2e-4, min = 0, vary = True)
#    #    if meas.echotype == ECHO_NONE:
#    #
#    #        params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)  #Changed to plus sign for accommodate for amplitude RO, need a good LT solution
#    #
#    #    elif meas.echotype == ECHO_HAHN:
#    #        params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi) #DARIO added to fit better for echo vs plain T2
#        if ys[0] < np.average(ys):
#            params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)
#        else:
#            params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True) #Yingying changed phi0 to checking value of first point
#        result = lmfit.minimize(changing_freq_fit, params, args=(xs, ys))
#    #    lmfit.report_fit(params)
#    #    result2 = lmfit.minimize(t2_fit, result.params, args=(xs,ys))
#        lmfit.report_fit(result.params)
#    
#    
#        fig.axes[0].plot(xs/1e3, -changing_freq_fit(result.params, xs, 0), 
#                label='Fit, tau=%.03f us, df=%.03f kHz, df_final = %.03f kHz,\n df_average = %.03f kHz\n tau_i = %.04f us, tau_f = %.04f us, tau_ave = %.04f us'%(
#                        result.params['tau'].value/1000, 
#                        result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[0]*result.params['slope']),
#                        result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[-1]*result.params['slope']),
#                        np.average(result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs*result.params['slope'])),
#                        0.001/((1/result.params['tau'].value) + result.params['A2'].value*np.exp(-xs[0]*result.params['slope'].value/2)),
#                        0.001/((1/result.params['tau'].value) + result.params['A2'].value*np.exp(-xs[-1]*result.params['slope'].value/2)),
#                        0.001/np.average((1/result.params['tau'].value) + result.params['A2'].value*np.exp(-xs*result.params['slope'].value/2))                   
#                        ))
#        fig.axes[0].legend()
#        fig.axes[0].set_ylabel('Intensity [AU]')
#        fig.axes[0].set_xlabel('Time [us]')
#        fig.axes[1].plot(xs/1e3, changing_freq_fit(result.params, xs, ys), marker='s')
#        fig.canvas.draw()
        
        labels = ['phase 0','phase pi','averaged phase']

        for l in range(seq_num+1):
            ys = ys_als[l]
            
            amp0 = (np.max(ys) - np.min(ys)) / 2
            fftys = np.abs(np.fft.fft(ys - np.average(ys)))
            fftfs = np.fft.fftfreq(len(ys), np.abs(xs[1]-xs[0]))
            f0 = np.abs(fftfs[np.argmax(fftys)])
            print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)
        
            params = lmfit.Parameters()
            params.add('ofs', value=np.average(ys))
            params.add('amp', value=amp0, min=0.1)
            params.add('tau', value=max(xs)*0.6, min=1, max=2e5)
            params.add('freq', value=0.055, min=0, max = 0.07)
            params.add('slope', value=0,vary = False)
            params.add('A', value = 0, vary = False)
            params.add('A2', value = 0, vary = False)
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
#            freqs[l][j] = result.params['freq'].value
#            taus[l][j] = result.params['tau'].value
#            return_result.append(result.params)
            
            residues = changing_freq_fit(result.params, xs, ys)
            amp0 = (np.max(residues) - np.min(residues)) / 2
            fftys = np.abs(np.fft.fft(residues - np.average(residues)))
            fftfs = np.fft.fftfreq(len(residues), xs[1]-xs[0])
            f0 = np.abs(fftfs[np.argmax(fftys)])
            print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)
    
            params2 = lmfit.Parameters()
            params2.add('ofs', value=amp0)
            params2.add('amp', value=amp0, min=0)
            params2.add('tau', value=xs[-1], min=10, max=200000)
            params2.add('freq', value=f0, min=0)
            params2.add('phi0', value=-np.pi/2.0, min=-1.5*np.pi, max=1.5*np.pi)
            result = lmfit.minimize(t2_fit, params2, args=(xs, residues))
            lmfit.report_fit(result.params)
    #        fig.axes[1].plot(xs/1e3, -t2_fit(result.params, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz'%(result.params['tau'].value/1000, result.params['freq'].value*1e6))
#            fig.axes[1].legend()
    
            params3 = lmfit.Parameters()
            params3.add('ofs', value=params['ofs'].value)
            params3.add('amp', value=params['amp'].value, min=0, max=params['amp'].value*2)
            params3.add('tau', value=params['tau'].value, min=10, max=200000)
            params3.add('freq', value=params['freq'].value , min=0, max=20e-2)
            params3.add('phi0', value=params['phi0'].value, min=-1.2*np.pi, max=1.2*np.pi)
            params3.add('amp2', value=result.params['amp'].value, min=0, max=params['amp'].value*2)
    #        params3.add('tau2', value=result.params['tau'].value, min=10, max=200000)
            params3.add('freq2', value=result.params['freq'].value, min=0, max=20e-2)
            params3.add('phi2', value=result.params['phi0'].value, min=-1.5*np.pi, max=1.5*np.pi)
    
            result = lmfit.minimize(double_sin_fit, params3, args=(xs,ys))
            lmfit.report_fit(result.params)
            
            freqs[l][j] = result.params['freq'].value
            taus[l][j] = result.params['tau'].value
            text = 'Fit, tau1=%.03f us, df1=%.03f kHz, amp1=%.02f \nFit, tau2=%.03f us, df2=%.03f kHz, amp2=%.02f'%(result.params['tau'].value/1000, result.params['freq'].value*1e6, result.params['amp'].value, result.params['tau'].value/1000, result.params['freq2'].value*1e6, result.params['amp2'].value)
            fig.axes[0].plot(xs/1e3, -double_sin_fit(result.params, xs, 0), label=text)
            fig.axes[0].legend()
            fig.axes[0].set_ylabel('Intensity [AU]')
            fig.axes[0].set_xlabel('Time [us]')
#            fig.axes[1].plot(xs/1e3, double_sin_fit(result.params, xs, ys), marker='s')
            fig.canvas.draw()
            
            
            
##            if meas.double_freq == False:
#            fig.axes[0].plot(xs/1e3, -changing_freq_fit(result.params, xs, 0), 
#                    label='Fit, tau=%.03f us, df=%.03f kHz, %s'%(
#                            result.params['tau'].value/1000,
#                            result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[0]*result.params['slope']),
##                            result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[-1]*result.params['slope'])))
#                            labels[l]))
#            fig.axes[0].legend()
#            fig.axes[0].set_ylabel('Intensity [AU]')
#            fig.axes[0].set_xlabel('Time [us]')
##            fig.axes[1].plot(xs/1e3, changing_freq_fit(result.params, xs, ys), marker='s')
#            fig.canvas.draw()
#        if j >0:            
#            pl.close()
        j = j + 1
            
if repeat >1:
    if CW_qubit == True:
        pl.figure()
        pl.title('field = %s T'%(field))
        labels = ['phase 0','phase pi','averaged phase']
        freq = freqs
        for l in range(seq_num +1):
            pl.plot(freq[l]*1000, label = labels[l] + ' w/o qubit, ave freq = %.3f +/- %.3f MHz'%(
                    np.average(freq[l]*1000), np.std(freq[l])/np.sqrt(len(freq[l]))*1000))

        pl.legend()  
        pl.figure()
        pl.title('field = %s T'%(field))
        labels = ['phase 0','phase pi','averaged phase']
        freq = freqs
        for l in range(seq_num +1):
            pl.plot(taus[l]*1000, label = labels[l] + ' w/o qubit, ave tau = %.3f +/- %.3f MHz'%(
                    np.average(taus[l]*1000), np.std(taus[l])/np.sqrt(len(taus[l]))*1000))

        pl.legend()
        
        
        pl.figure()

        pl.plot(freq[l]*1000, 1/taus[l]*1000, label = labels[l])

        pl.legend()
        
        data_to_save = np.concatenate([freqs[l], taus[l]])
        
        if save_data:
            main_filepath = 'C:\\Users\\Wang_Lab\\Documents\\circulator results\\01052021cooldown_circulator\\CW_ramsey\\'
            end_time = list(str(datetime.datetime.now())[:19])
            end_time[13] = '-'
            end_time[16] = '-'
            time_stamp =''.join(end_time)
            save_filepath = main_filepath 
            
            
            if not os.path.exists(save_filepath):
                os.makedirs(save_filepath)
                

            np.savetxt(save_filepath + ' %s_%sT_results.txt'%(time_stamp,field), data_to_save)
    else:
        
        pl.figure()
        pl.title('field = %s T'%(field))
        labels = ['phase 0','phase pi','averaged phase']
        freq = freqs[:,0::2]
        freq_q = freqs[:,1::2]
        for l in range(seq_num +1):
            pl.plot(freq[l]*1000, label = labels[l] + ' w/o qubit, ave freq = %.3f +/- %.3f MHz'%(
                    np.average(freq[l]*1000), np.std(freq[l])/np.sqrt(len(freq[l]))*1000))
            pl.plot(freq_q[l]*1000, label = labels[l] + ' w/ qubit, ave freq = %.3f +/- %.3f MHz'%(
                    np.average(freq_q[l]*1000), np.std(freq_q[l])/np.sqrt(len(freq_q[l]))*1000))
        pl.legend()

