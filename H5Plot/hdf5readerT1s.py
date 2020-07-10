# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 15:24:15 2020

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



def exp_decay(params, x, data):
    est = params['ofs'] + params['amplitude'] * np.exp(-x / params['tau'].value)
    return data - est



''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '1122cooldown_Circulator_cavity - Copy (2).hdf5'
date = '20200211'
#experiment = 'ROCavSpectroscopy_keysight'
f = h5.File(filepath + hdf5_name, 'r')
j =0
#
fields = np.linspace(1,40,41)
nrows = 2 
t1 = np.zeros([nrows,len(fields)])

t1_err = np.zeros([nrows,len(fields)])


for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if int(title[0:6]) <= int('160000') and int(title[0:6]) > int('120220') and (title[7:9] =='T1' or title[7:9] =='FT'):
        print title



        x_key = 'delays'
        #x2_key = 'powers'
        exp = f[date][title]
        y_keys = exp.keys()
        
            
        xs = exp[x_key].value
#        amp = exp['amplitudes'].value[0]
        phase = exp['avg_pp'].value
        
#        freqs = freqs[40:100]
#        amp = amp[40:100]
#        phase = phase[40:100]
        ys = phase
            
        fig = pl.figure()
        fig.add_subplot(111)
        fig.axes[0].plot(xs/1e3,ys)
        #fig.axes[1].plot(freqs/1e6,phase)
#        params = lmfit.Parameters()
        
        
        #f = h5.File(filepath + hdf5_name, 'r')
        #
        #expgroup = f['/' + date]
        
        #cut_freq = None
        
        
            

    
        params = lmfit.Parameters()
        params.add('ofs', value=np.min(ys))
        params.add('amplitude', value=np.max(ys)-np.min(ys))
        params.add('tau', value=len(xs)*1000/4.0, min=0)
        result = lmfit.minimize(exp_decay, params, args=(xs, ys))
#        lmfit.report_fit(result.params)
    
        fig.axes[0].plot(xs/1e3, -exp_decay(result.params, xs, 0), label='Fit, tau = %.03f us +/- %.03f us'%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
        fig.axes[0].legend(loc=0)
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Time [us]')
    
#        fig.axes[1].plot(xs, exp_decay(result.params, xs, ys), marker='s')

        t1[j%nrows][j/nrows] = result.params['tau'].value
        t1_err[j%nrows][j/nrows] = result.params['tau'].stderr

        j = j+1
        fn = os.path.join(r'C:\Users\Wang_Lab\Documents\yingying\11222019cooldown', 'fitting\%s_%s.png'%(title,j-1))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        pl.savefig(fn, **kwargs)
        pl.close()
    #fig.axes[1].set_aspect('equal', 'box')
f.close()

for k in []:
    freq1[k%nrows][k/nrows] = 0
    freq1_err[k%nrows][k/nrows] = 10000000
    freq2[k%nrows][k/nrows] = 0
    freq2_err[k%nrows][k/nrows] = 10000000
pl.figure()

pl.errorbar(fields, t1[0],yerr = t1_err[0],fmt = 'o', label = 'T1')
pl.errorbar(fields, t1[1],yerr = t1_err[1],fmt = 'o', label = 'FT1')



pl.legend()



#pl.figure()
#
#pl.errorbar(fields, freq1[1] - freq1[0], yerr = freq1_err[1] + freq1_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.711GHz mode')
#pl.errorbar(fields, freq1[2] - freq1[0], yerr = freq1_err[2] + freq1_err[0], fmt = 'o',label = 'chi between qubit 2 f and 10.711GHz mode')
#pl.errorbar(fields, freq2[1] - freq2[0], yerr = freq2_err[1] + freq2_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.718GHz mode')
#pl.errorbar(fields, freq2[2] - freq2[0], yerr = freq2_err[2] + freq2_err[0], fmt = 'o',label = 'chi between qubit 2 f and 10.718GHz mode')
#pl.ylim(-1.5e6,0.5e6)
#pl.legend()
#
#pl.figure()
#
##pl.errorbar(fields, freq1[1] - freq1[0], yerr = freq1_err[1] + freq1_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.711GHz mode')
#pl.scatter(fields, (freq1[2]-freq1[0])/(freq1[1]-freq1[0]),label = 'chi qubit 2 e f and 10.711GHz mode')
##pl.errorbar(fields, freq2[1] - freq2[0], yerr = freq2_err[1] + freq2_err[0], fmt = 'o',label = 'chi between qubit 2 e and 10.718GHz mode')
#pl.scatter(fields, (freq2[2]-freq2[0])/(freq2[1]-freq2[0]),label = 'chi qubit 2 e f and 10.718GHz mode')
##pl.ylim(-1.5e6,0.5e6)
#pl.legend()





#to_save = [freq1, freq1_err, freq2, freq2_err]
#
#with file('C:\Users\Wang_Lab\Documents\yingying\\11222019cooldown\\fitting\\fitting_result.txt','w') as outfile:
#
#    outfile.write('# Array\n')
#
#    # Iterating through a ndimensional array produces slices along
#    # the last axis. This is equivalent to data[i,:,:] in this case
#    for data_slice in to_save:
#
#        # The formatting string indicates that I'm writing out
#        # the values in left-justified columns 7 characters in width
#        # with 2 decimal places.  
#        np.savetxt(outfile, data_slice, fmt='%-7.7f')
#
#        # Writing out a break to indicate different slices...
#        outfile.write('# New slice\n')


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