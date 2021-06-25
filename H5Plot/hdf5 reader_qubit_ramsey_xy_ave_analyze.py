# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 15:57:40 2021

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 16:38:00 2020

@author: Wang_Lab
"""

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
import datetime

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
    diff =  data - est
    for i in range(int(len(diff)/10)):
        diff[i] = 5*diff[i]
    return diff

def changing_freq_fit_plot(params, x, data):
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
    return (data - est)

if 1: #average and save data
    ''' Path to the .hdf5 file '''
    filepath = 'C:/_Data/'
    hdf5_name = '04222021cooldown_circulator - Copy.hdf5'
    date = '20210624'
    #date = '20210301'
    save_data = True
    #experiment = 'ROCavSpectroscopy_keysight'
    #experiment = 'Power_Sweep_VNA'
    if save_data:
        main_filepath = 'C:\\Users\\Wang_Lab\\Documents\\circulator results\\06062021cooldown_circulator\\sigma_xy_qubit2\\'
        end_time = list(str(datetime.datetime.now())[:19])
        end_time[13] = '-'
        end_time[16] = '-'
        time_stamp =''.join(end_time)
        save_filepath = main_filepath 
        
        
        if not os.path.exists(save_filepath):
            os.makedirs(save_filepath)
            
    f = h5.File(filepath + hdf5_name, 'r')
    j = 0
    
    end_val_ind = 100
    pts = 242
    
    field = -0.04
    #base = False
    #base = True
    
    nrows = 2
    fix_phi0 = None
    
    base_avg_factor = 5
    avg_factor = 5
            
    if j == 0:
        freqs = np.zeros([nrows,2])
        taus = np.zeros([nrows,2])
        end_val = np.zeros([2])
        
    if base_avg_factor is not 0:
        base_avg_data_array = np.zeros((base_avg_factor,pts),dtype = 'complex128')
    if avg_factor is not 0:
        avg_data_array = np.zeros((avg_factor,pts),dtype = 'complex128')
    #if three_modes:
    #    if j == 0:
    #        freq1 = np.zeros([nrows,len(fields)])
    #        freq2 = np.zeros([nrows,len(fields)])
    exp_t = 'Ramsey_Measurement_mixer_xy'
    
    for i, title in enumerate(f[date].keys()):
    #    print int(title[0:6])
    #    print int(title[0:6]) <= 020617
        if int(title[0:6]) <= int('045200') and int(title[0:6]) > int('022000')  and title[7:] == exp_t:# and title[7:12] =='ROCav':
            print 'j = %s'%(j)
            print title
    
    
    #        if j < base_avg_factor:
    #            print 'saving data'
                
            x_key = 'delays'
            #x2_key = 'powers'
            exp = f[date][title]
    #            y_keys = exp.keys()
            
                
            delays = exp[x_key].value
           
            comp_data_trial = exp['avg'].value
            phase_data = exp['avg_pp'].value
            
            if j < base_avg_factor:
                base_avg_data_array[j] = comp_data_trial
            else:
                avg_data_array[j - base_avg_factor] = comp_data_trial
                
            j = j + 1
                    
    f.close()          
    
    base_avg_data = np.zeros(pts, dtype = 'complex128')
    avg_data = np.zeros(pts, dtype = 'complex128')
    for k in range(len(avg_data)):
        if base_avg_factor is not 0:
            base_avg_data[k] = np.average(np.transpose(base_avg_data_array)[k])
        if avg_factor is not 0:
            avg_data[k] = np.average(np.transpose(avg_data_array)[k])
    
    #comp_data = avg_data
    
    if base_avg_factor is not 0:
        comp_data = base_avg_data
        pl.figure('complex plane')
        pl.scatter(np.real(comp_data),np.imag(comp_data), label = '%s'%(i))
        p = np.polyfit(np.real(comp_data), np.imag(comp_data), 1)
        pl.plot(np.linspace(np.min(np.real(comp_data)), np.max(np.real(comp_data)), 11), 
                p[0] * np.linspace(np.min(np.real(comp_data)), np.max(np.real(comp_data)), 11) + p[1])
        
        vec = np.array([1,p[0]])/np.sqrt(1 + p[0]**2)
        data_o = comp_data - np.average(comp_data)
        data_vec = np.vstack((np.real(data_o),np.imag(data_o)))
        proj_b = np.matmul(vec, data_vec)
        
        
        
        #        center = np.mean(comp_data)
        #        v_1 = comp_data[np.argmax()]
        seq_num = 2
        xs = delays
        ys_als = np.zeros([seq_num , len(xs)])
        #        ys_als[0] = phase_data.value[0::seq_num]
        #        ys_als[1] = phase_data.value[1::seq_num]
        ys_als[0] = proj_b[0::seq_num]
        ys_als[1] = proj_b[1::seq_num]
        
        fig = pl.figure()
        fig.add_subplot(111)
        #        gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
        fig.axes[0].scatter(xs/1e3, ys_als[0])
        fig.axes[0].scatter(xs/1e3, ys_als[1])
        fig.axes[0].plot(xs/1e3, np.sqrt(ys_als[0]**2 + ys_als[1]**2))
        
        #        fig.add_subplot(132)
        #        fig.axes[1].plot(freqs/1e6,phase)
        
        params = lmfit.Parameters()
        
        
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
            params.add('amp', value=amp0, min=0.01)
            params.add('tau', value=max(xs)*0.7, min=1, max=2e5)
            params.add('freq', value=f0, min=0)
            params.add('slope', value = 0.005,min = 0, vary = False)#value=0,vary = False)
            params.add('A', value = -0.001, max = 0, min = -0.01)#value = 0, vary = False)
            params.add('A2', value = 0.001, min = 0)#value = 0, vary = False)
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
    #        freqs[l][j//avg_factor] = result.params['freq'].value
    #        taus[l][j//avg_factor] = result.params['tau'].value
        #            return_result.append(result.params)
        #            if meas.double_freq == False:
            fig.axes[0].plot(xs/1e3, -changing_freq_fit_plot(result.params, xs, 0), 
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
        
        pl.figure('%s T envelope graph'%(field))
        pl.title('envelope graph')
        pl.plot(xs, np.sqrt((ys_als[0]-offset)**2 + (ys_als[1]-offset)**2)/norm_scale)
        pl.plot(xs, (ys_als[0]-offset)/norm_scale, label = 'sigma x w/o cavity photon')
        pl.plot(xs, (ys_als[1]-offset)/norm_scale, label = 'sigma y w/o cavity photon')
        pl.xlabel('Time(nanoseconds)')
        pl.ylabel('<\u03C3>')
        pl.legend(loc=1, prop={'size': 12})
        
        
        angle_data = np.arctan((ys_als[1]-offset)/(ys_als[0]-offset))
        
        for i in range(len(angle_data)-1):
            if angle_data[i+1] < (angle_data[i]-.75*np.pi/2):
                angle_data[i+1:] = angle_data[i+1:] + np.pi
        pl.figure('%s T accumulated phase'%(field))
        pl.title('accumulated phase')
        pl.plot(xs/1e3, angle_data, label = 'w/o cavity photon')
        pl.xlabel('Time(microseconds)')
        pl.ylabel('Phase')
        pl.legend()
        #        if j >0:            
        #            pl.close()
        proj_b_renorm = (proj_b-offset)/norm_scale
        if save_data:
            np.savetxt(save_filepath + ' %s_%sT_base_results.txt'%(time_stamp,field), proj_b_renorm)
    
    if avg_factor is not 0:
        comp_data = avg_data
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
            params.add('amp', value=amp0, min=0.01)
            params.add('tau', value=max(xs)*0.7, min=1, max=2e5)
            params.add('freq', value=f0, min=0)
            params.add('slope', value = 0.005,min = 0, vary = False)#value=0,vary = False)
            params.add('A', value = -0.001, max = 0, min = -0.01)#value = 0, vary = False)
            params.add('A2', value = 0.001, min = 0)#value = 0, vary = False)
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
    #        freqs[l][j//avg_factor] = result.params['freq'].value
    #        taus[l][j//avg_factor] = result.params['tau'].value
        #            return_result.append(result.params)
        #            if meas.double_freq == False:
            fig.axes[0].plot(xs/1e3, -changing_freq_fit_plot(result.params, xs, 0), 
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
        
        pl.figure('%s T envelope graph'%(field))
        pl.title('envelope graph')
        pl.plot(xs, np.sqrt((ys_als[0]-offset)**2 + (ys_als[1]-offset)**2)/norm_scale, label = 'env, w/ cavity photon')
        pl.plot(xs, (ys_als[0]-offset)/norm_scale, label = 'sigma x, w/ cavity photon')
        pl.plot(xs, (ys_als[1]-offset)/norm_scale, label = 'sigma y, w/ cavity photon')
        pl.xlabel('Time(nanoseconds)')
        pl.ylabel('<\u03C3>')
        pl.legend(loc=1, prop={'size': 12})
        
        
        angle_data = np.arctan((ys_als[1]-offset)/(ys_als[0]-offset))
        
        for i in range(len(angle_data)-1):
            if angle_data[i+1] < (angle_data[i]-.75*np.pi/2):
                angle_data[i+1:] = angle_data[i+1:] + np.pi
        pl.figure('%s T accumulated phase'%(field))
        pl.title('accumulated phase')
        pl.plot(xs/1e3, angle_data, label = 'with cavity photon')
        pl.xlabel('Time(microseconds)')
        pl.ylabel('Phase')
        pl.legend()
        proj_renorm = (proj-offset)/norm_scale
        
        if save_data:
            np.savetxt(save_filepath + ' %s_%sT_results.txt'%(time_stamp,field), proj_renorm)
 
if 1: # analyzing qubit shift and decay
    proj_data = proj_renorm
    proj_base = proj_b_renorm
    sigma_x = proj_data[::2]
    sigma_y = proj_data[1::2]
    
    sigma_x_b = proj_base[::2]
    sigma_y_b = proj_base[1::2]
    
    env = np.sqrt(sigma_x**2 + sigma_y**2)
    
    env_base = np.sqrt(sigma_x_b**2 + sigma_y_b**2)
    #env_base[9] = 1
    #
    #env = env/env_base

    
    delay = 60
    sigma_raw = env[delay-5:delay + 5]
    
    sigma = np.average(sigma_raw)
    sigma_stdv = np.std(sigma_raw)/3
    print('delay', delay, 'delays[delay]',delays[delay])
    print('decay rate', -np.log(sigma)/(delays[delay]) * 1000, '+/-',(np.std(sigma_raw)/np.sqrt(10))/sigma/(delays[delay])*1000)
    
    angle_data = np.arctan((sigma_y)/sigma_x)    
    for i in range(len(angle_data)-1):
        if angle_data[i+1] < (angle_data[i]-.75*np.pi/2):
            angle_data[i+1:] = angle_data[i+1:] + np.pi
                
    angle_base = np.arctan((sigma_y_b)/sigma_x_b)
    for i in range(len(angle_base)-1):
        if angle_base[i+1] < (angle_base[i]-.75*np.pi/2):
            angle_base[i+1:] = angle_base[i+1:] + np.pi
                
    angle_data = angle_base - angle_data
    pl.figure()
    pl.plot(delays, angle_data)
    angle = angle_data[delay-5:delay+5] - angle_data[0]
    angle_plot = np.mean(angle)
    freq_stdv = np.std(angle)/(3*2*np.pi*delays[delay]) * 1000
    freq = angle_plot/(2*np.pi*delays[delay]) * 1000
    
    print('shift freq', freq, '+/-',freq_stdv)
