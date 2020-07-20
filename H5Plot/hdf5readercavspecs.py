# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 11:47:21 2020

@author: Wang_Lab
"""

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

def S21_three_modes(params, x, y):
    est = np.sqrt(params['kappa_prod1'])/(-1j*(x-params['omega_c'])-(params['kappa_a1'])/2.0 )* np.exp(1j*params['phi1'])
    est = est + np.sqrt(params['kappa_prod2'])/(-1j*(x-params['omega_c2'])-(params['kappa_a2'])/2.0 ) * np.exp(1j*(params['phi21']+params['phi1']))
    est = est + np.sqrt(params['kappa_prod3'])/(-1j*(x-params['omega_c3'])-(params['kappa_a3'])/2.0 ) * np.exp(1j*(params['phi31']+params['phi1']))
    est = est * np.exp(1j* params['slope'] * x)
    if np.max(np.abs(y)) < limit_for_off:
            est = est + params['roff'] + 1j*params['ioff']
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2) 

''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '0626cooldown_circualtor - Copy (2).hdf5'
date = '20200717'
experiment = 'ROCavSpectroscopy_keysight'
f = h5.File(filepath + hdf5_name, 'r')
j = 0
#
three_modes = False
two_modes = True

fields = np.linspace(0,0.05,6)
nrows = 2
if two_modes:
    if j == 0:
        freq1 = np.zeros([nrows,len(fields)])
        freq2 = np.zeros([nrows,len(fields)])
        freq1_err = np.zeros([nrows,len(fields)])
        freq2_err = np.zeros([nrows,len(fields)])
if three_modes:
    if j == 0:
        freq1 = np.zeros([nrows,len(fields)])
        freq2 = np.zeros([nrows,len(fields)])
        freq3 = np.zeros([nrows,len(fields)])
        freq1_err = np.zeros([nrows,len(fields)])
        freq2_err = np.zeros([nrows,len(fields)])
        freq3_err = np.zeros([nrows,len(fields)])

for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if int(title[0:6]) <= int('240000') and int(title[0:6]) > int('170000') and title[7:12] =='ROCav':
        print title



        x_key = 'freqs'
        #x2_key = 'powers'
        exp = f[date][title]
        y_keys = exp.keys()
        
            
        freqs = exp[x_key].value
        amp = exp['amplitudes'].value[0]
        phase = exp['phases'].value[0]
        
#        freqs = freqs[40:100]
#        amp = amp[40:100]
#        phase = phase[40:100]
        datas = amp * np.exp(1j * phase *np.pi/180)
            
        fig = pl.figure()
        fig.add_subplot(131)
        fig.axes[0].plot(freqs/1e6,amp,label = '-6dB')
        fig.add_subplot(132)
#        fig.axes[1].plot(freqs/1e6,phase)
        params = lmfit.Parameters()
        
        
        #f = h5.File(filepath + hdf5_name, 'r')
        #
        #expgroup = f['/' + date]
        
        #cut_freq = None
        
        
        if two_modes:    
            params = lmfit.Parameters()
            params.add('kappa_prod1', value= 3.28e12, min = 0)#,vary = False)
            params.add('omega_c', value=10.808e9)#,vary = False)
            params.add('kappa_a', value=2e6, min = 0)#,vary = False)
            if np.max(np.abs(datas)) < limit_for_off:
                params.add('roff',value =(datas[0].real+ datas[-1].real)/2)
                params.add('ioff',value = (datas[0].imag+ datas[-1].imag)/2)
            params.add('phi1',value = 1.15, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
                    
            
            params.add('kappa_prod2', value= 6.185e14, min = 0)#,vary = False)
            params.add('omega_c2', value=10.83e9)#,vary = False)
            params.add('kappa_a2', value=8e5, min = 0)#,vary = False)
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
            fig.add_subplot(133)
            fig.axes[2].plot(datas_p.real,datas_p.imag)  
            fig.axes[1].plot(freqs/float(1e6),phase_p%360)  
            fig.axes[0].plot(freqs/float(1e6), np.abs(fitdata),'--' )
            fig.axes[1].plot(freqs/float(1e6),(np.angle(fitdata, deg = True)-freqs*result.params['slope']*180/np.pi)%360, '--') 
            fitdata_p = np.abs(fitdata) * np.exp(1j * (np.angle(fitdata)-freqs*result.params['slope']))
            fig.axes[2].plot(fitdata_p.real,fitdata_p.imag, '--')
            pl.xlabel('freq(MHz)')
    
            freq1[j%nrows][j/nrows] = result.params['omega_c'].value
            freq1_err[j%nrows][j/nrows] = result.params['omega_c'].stderr
            freq2[j%nrows][j/nrows] = result.params['omega_c2'].value      #np.average(ys)
            freq2_err[j%nrows][j/nrows] =result.params['omega_c2'].stderr
            j = j+1
            fn = os.path.join(r'C:\Users\Wang_Lab\Documents\yingying\03172020cooldown', 'fitting\%s_%s.png'%(title,j-1))
            fdir = os.path.split(fn)[0]
            if not os.path.isdir(fdir):
                os.makedirs(fdir)
            kwargs = dict()
            pl.savefig(fn, **kwargs)
        if three_modes:
            params = lmfit.Parameters()
            params.add('kappa_prod1', value= .288e14, min = 0)#,vary = False)
            params.add('omega_c', value=10.803e9)#,vary = False)
            params.add('kappa_a1', value=14.5e6, min = 0)#,vary = False)
            if np.max(np.abs(datas)) < limit_for_off:
                params.add('roff',value =(datas[0].real+ datas[-1].real)/2)
                params.add('ioff',value = (datas[0].imag+ datas[-1].imag)/2)
            params.add('phi1',value = 2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
                    
            
            params.add('kappa_prod2', value= 6.1835e12, min = 0)#,vary = False)
            params.add('omega_c2', value=10.808e9)#,vary = False)
            params.add('kappa_a2', value=1.27e6, min = 0)#,vary = False)
            params.add('phi21',value = 1.33, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
        
            params.add('kappa_prod3', value= 1e11, min = 0)#,vary = False)
            params.add('omega_c3', value=10.82e9)#,vary = False)
            params.add('kappa_a3', value = 50e6, min = 0)#,vary = False)
            params.add('phi31',value =-2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
            params.add('slope', value = -4.3e-7)
        #    if itime == 0:
        #        params = lmfit.Parameters()
        #        params.add('kappa_prod1', value= 1e9, min = 0)#,vary = False)
        #        params.add('omega_c', value=10.711e9)#,vary = False)
        #        params.add('kappa_a', value=2e6, min = 0)#,vary = False)
        #        if np.max(np.abs(datas)) < limit_for_off:
        #            params.add('roff',value =(datas[itime][0].real+ datas[itime][-1].real)/2,vary = False)
        #            params.add('ioff',value = (datas[itime][0].imag+ datas[itime][-1].imag)/2, vary = False)
        #        params.add('phi1',value = -3, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
        #                
        #    
        #        params.add('kappa_prod2', value= 3e9, min = 0)#,vary = False)
        #        params.add('omega_c2', value=10.711e9)#,vary = False)
        #        params.add('kappa_a2', value=1.5e6, min = 0)#,vary = False)
        #        params.add('phi21',value = 4.2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
            result = lmfit.minimize(S21_three_modes, params, args=(freqs, datas))
            lmfit.report_fit(result.params)
            fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a1'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
            if np.max(np.abs(datas)) < limit_for_off:
                fitdata1 = fitdata1 + result.params['roff'].value + 1j*result.params['ioff'].value
            fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
            fitdata3 = np.sqrt(result.params['kappa_prod3'].value)/(-1j*(freqs-result.params['omega_c3'].value)-(result.params['kappa_a3'].value)/2.0 )* np.exp(1j*(result.params['phi31'].value + result.params['phi1'].value))
            fitdata = fitdata1 + fitdata2 + fitdata3
            fitdata = fitdata * np.exp(1j * result.params['slope']*freqs)
            if np.max(np.abs(datas)) < limit_for_off:
                fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
            
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
    
            freq1[j%nrows][j/nrows] = result.params['omega_c'].value
            freq1_err[j%nrows][j/nrows] = result.params['omega_c'].stderr
            freq2[j%nrows][j/nrows] = result.params['omega_c2'].value      #np.average(ys)
            freq2_err[j%nrows][j/nrows] =result.params['omega_c2'].stderr
            freq3[j%nrows][j/nrows] = result.params['omega_c3'].value      #np.average(ys)
            freq3_err[j%nrows][j/nrows] =result.params['omega_c3'].stderr
            j = j+1
            fn = os.path.join(r'C:\Users\Wang_Lab\Documents\yingying\03172020cooldown', 'fitting\%s_%s.png'%(title,j-1))
            fdir = os.path.split(fn)[0]
            if not os.path.isdir(fdir):
                os.makedirs(fdir)
            kwargs = dict()
            pl.savefig(fn, **kwargs)
#            fig.axes[0].plot(freqs/float(1e9), np.abs(fitdata),'--' )
#            fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
#        pl.close()
    #fig.axes[1].set_aspect('equal', 'box')
f.close()

for k in []:
    freq1[k%nrows][k/nrows] = 0
    freq1_err[k%nrows][k/nrows] = 10000000
    freq2[k%nrows][k/nrows] = 0
    freq2_err[k%nrows][k/nrows] = 10000000
pl.figure()

pl.errorbar(fields, freq1[0],yerr = freq1_err[0],fmt = 'o', label = 'g')
pl.errorbar(fields, freq1[1],yerr = freq1_err[1],fmt = 'o', label = 'qubit 2 in e')
#pl.errorbar(fields, freq1[2],yerr = freq1_err[2],fmt = 'o',label = 'qubit 2 in e')
pl.errorbar(fields, freq2[0],yerr = freq2_err[0],fmt = 'o', label = 'g')
pl.errorbar(fields, freq2[1],yerr = freq2_err[1],fmt = 'o', label = 'qubit 2 in e')
#pl.errorbar(fields, freq2[2],yerr = freq2_err[2], fmt = 'o',label = 'qubit 2 in e')
pl.ylim(10.809e9,10.825e9)
pl.legend()

fn = os.path.join(r'C:\Users\Wang_Lab\Documents\yingying\03172020cooldown', 'fitting\\freqs.png')
fdir = os.path.split(fn)[0]
if not os.path.isdir(fdir):
    os.makedirs(fdir)
kwargs = dict()
pl.savefig(fn, **kwargs)

pl.figure()

pl.errorbar(fields, freq1[1] - freq1[0], yerr = freq1_err[1] + freq1_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.711GHz mode')
#pl.errorbar(fields, freq1[2] - freq1[0], yerr = freq1_err[2] + freq1_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.711GHz mode')
pl.errorbar(fields, freq2[1] - freq2[0], yerr = freq2_err[1] + freq2_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.718GHz mode')
#pl.errorbar(fields, freq2[2] - freq2[0], yerr = freq2_err[2] + freq2_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.718GHz mode')
pl.ylim(-1.5e6,0.5e6)
pl.legend()

fn = os.path.join(r'C:\Users\Wang_Lab\Documents\yingying\03172020cooldown', 'fitting\\chis.png')
fdir = os.path.split(fn)[0]
if not os.path.isdir(fdir):
    os.makedirs(fdir)
kwargs = dict()
pl.savefig(fn, **kwargs)
#pl.figure()
#
##pl.errorbar(fields, freq1[1] - freq1[0], yerr = freq1_err[1] + freq1_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.711GHz mode')
#pl.scatter(fields, (freq1[2]-freq1[0])/(freq1[1]-freq1[0]),label = 'chi qubit 2 e f and 10.711GHz mode')
##pl.errorbar(fields, freq2[1] - freq2[0], yerr = freq2_err[1] + freq2_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.718GHz mode')
#pl.scatter(fields, (freq2[2]-freq2[0])/(freq2[1]-freq2[0]),label = 'chi qubit 2 e f and 10.718GHz mode')
##pl.ylim(-1.5e6,0.5e6)
#pl.legend()





to_save = [freq1, freq1_err, freq2, freq2_err]

with file('C:\Users\Wang_Lab\Documents\yingying\\03172020cooldown\\fitting\\fitting_result.txt','w') as outfile:

    outfile.write('# Array\n')

    # Iterating through a ndimensional array produces slices along
    # the last axis. This is equivalent to data[i,:,:] in this case
    for data_slice in to_save:

        # The formatting string indicates that I'm writing out
        # the values in left-justified columns 7 characters in width
        # with 2 decimal places.  
        np.savetxt(outfile, data_slice, fmt='%-7.7f')

        # Writing out a break to indicate different slices...
        outfile.write('# New slice\n')


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


#def linerfit(params, x, y):
#    est = params['slope'] * x + params['offset']
#    
#    return y - est
#    
#    
#    
#params = lmfit.Parameters()
#params.add('slope', value= 1e5)#,vary = False)
#params.add('offset', value=10.7108e9)#,vary = False)
#
#
#result = lmfit.minimize(linerfit, params, args=(fields, freq1[0]))
#lmfit.report_fit(result.params)
#pl.figure(97)
#pl.plot(fields, -linerfit(result.params, fields,0))