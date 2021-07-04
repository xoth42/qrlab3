# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 12:04:32 2020

@author: Wang_Lab
"""

import os
import time
import lmfit 



import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from matplotlib import gridspec


def Gaussfit(params, x, y):
    est = params['Amp'] * np.exp(-(x-params['freq'])**2/(2 * params['kappa']**2)) + params['off']
    
    return y - est

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '1122cooldown_Circulator_cavity - Copy (2).hdf5'

date = '20200117'
#date2 = '20191210'

#fields = np.linspace(0, 0.05,26)
#freqs = np.linspace(10.708,10.72,13)
freqs = np.linspace(1,20,20)

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'
datas = np.zeros([len(fields),1601],dtype = complex)


nrows = 2 
SS = np.zeros([nrows,len(freqs)])
SSn = np.zeros([nrows,len(freqs)])
SS_err = np.zeros([nrows,len(freqs)])
SSn_err = np.zeros([nrows,len(freqs)])  
amp = np.zeros([nrows,len(freqs)]) 
amp_err = np.zeros([nrows,len(freqs)])         
f = h5.File(filepath + hdf5_name, 'r')

j =0
for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if title[7:14] == 'SSBSpec' and int(title[0:6]) <= int('144558') and int(title[0:6]) >= int('132401'):
        print(title)
        exp = f[date][title]
        y_keys = list(exp.keys())
        xs = exp['detunings'].value
        data = exp['avg_pp'].value
        data_c = exp['avg'].value
        
    
    
    
    
        
        ys = data
        fig = pl.figure()
        fig.add_subplot(111)
        fig.axes[0].plot(xs/1e6,ys)
        
        params = lmfit.Parameters()
        
        
        #    if np.max(ys) + np.min(ys) < 2 * np.average(ys):
        if 1:
            params.add('Amp', value= -(np.max(ys)-np.min(ys)))
            params.add('freq', value=xs[np.argmin(ys)])
        else:
            
            params.add('Amp', value= (np.max(ys)-np.min(ys)))
            params.add('freq', value=xs[np.argmax(ys)])
        
        params.add('kappa', value=5e6, min = 0)#, max = 4e6)#,vary = False)
        params.add('off', value = np.average(ys))
        
                
        #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
        result = lmfit.minimize(Gaussfit, params, args=(xs,ys))
#        lmfit.report_fit(result.params)
        print(('fit freq: %s +/- %s  '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6)))
        
        
        fig.axes[0].plot(xs/1e6, -Gaussfit(result.params, xs, 0), label='fit freq: %s +/- %s MHz '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
        fig.axes[0].legend()
        
        
        
        #    
        #    fig.axes[0].plot(-xs/1e6, ys)
        fig.axes[0].set_xlabel('Detuning (MHz)')
        fig.axes[0].set_ylabel('Intensity (AU)')
        fig.canvas.draw()
#        pl.show()
#        time.sleep(1)
        pl.close()
        
        if j <nrows*len(freqs):
            SS[j%nrows][j/nrows] = result.params['freq'].value/1e6
            SS_err[j%nrows][j/nrows] = result.params['freq'].stderr/1e6
            amp[j%nrows][j/nrows] = result.params['off'].value      #np.average(ys)
            amp_err[j%nrows][j/nrows] =result.params['off'].stderr#np.sqrt( np.sum((ys+Gaussfit(result.params, xs, 0))**2/((len(ys)-1)*len(ys))))
        else:
            SSn[j%nrows][j/nrows-len(freqs)] = result.params['freq'].value/1e6
            SSn_err[j%nrows][j/nrows-len(freqs)] = result.params['freq'].stderr/1e6
        j = j+1
        
pl.figure()
for i in range(len(SS)):
    pl.errorbar(freqs,SS[i],yerr = SS_err[i])
pl.figure()
for i in range(len(SS)):
    pl.errorbar(freqs,amp[i],yerr = amp_err[i])
#pl.figure()
#for i in range(len(SS)):
#    pl.errorbar(freqs,SSn[i],yerr = SSn_err[i])
#        
#f.close()
#
#pl.figure()
#pl.errorbar(freqs, (SSn[2]-np.average(SSn[3]))/(SS[2]-np.average(SS[3])), yerr = np.sqrt((SS_err[2]/SS[2])**2 + (SSn_err[2]/SSn[2])**2),label = '%sT'%(fieldlist[k] ))
#pl.legend()


#field = 0.014
#k = int(np.where(fieldlist ==field)[0])
#SSdatap[k] = SS
#SSdatan[k] = SSn
#SSdatap_err[k] = SS_err
#SSdatan_err[k] = SSn_err

#pl.figure()
#for k in range(5):
#    n = SSdatan[k][2] - np.average(SSdatan[k][3])
#    p = SSdatap[k][2] - np.average(SSdatap[k][3])
#    pl.errorplot(freqs, n/p, yerr = np.sqrt((SS_errlabel = '%sT'%(fieldlist[k] ))
#    pl.legend()
##save data
#np.savez(r'C:\Users\Wang_Lab\Documents\yingying\SS', a = SSdatap, b = SSdatap_err, c = SSdatan, d = SSdatan_err)