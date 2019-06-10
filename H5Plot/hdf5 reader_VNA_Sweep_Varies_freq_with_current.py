# -*- coding: utf-8 -*-
"""
Created on Thu May 16 17:03:23 2019

@author: WangLab
"""

import os
import time
import lmfit 



import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from matplotlib import gridspec

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = 'FMR_RT_0515.hdf5'
#hdf5_name = 'FMR_RT_0515 - Copy.hdf5'
date = '20190530'
time = '155703'
#experiment = 'Power_Sweep_Varies_freq_VNA'
experiment = 'Current_Sweep_Varies_freq_VNA'
#experiment = 'Current_Sweep_VNA'
fit_S12 = True
fit_S11 = False
seperate_fitting_figure = True

#xlabel = 'current(mA)'
xlabel = 'different measurements'

def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est * np.exp(1j*params['phi'])
    
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    
    
def S11(params, x, y):

    est = (-1 - params['kappa_1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2))*params['A']
    return y - abs(est)


limit_for_off = 1

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = exp.keys()
#print(y_keys)

#y_keys.remove(x_key)
#y_keys.remove(x2_key)
freq = exp['freqs'].value
currents = exp['currents'].value

real = exp['realS21'].value
imag = exp['imaginaryS21'].value

'''Conversion factor from Yoko current in mA to actual magnetic field in mT'''
#if current.any() < 0.5:
#    field = current*529.37 + 0.49
#else:
#    field = -268.93 * (current)**2 + 839.69*current - 88.67

'''Plot'''
#pl.figure()
#figname = ''
#powerplot = np.concatenate((powers, np.zeros(1) + powers[1]-powers[0] + powers[-1]))
mag = 10*np.log10(real**2 + imag**2)
#Z = np.transpose(mag)
#X,Y = np.meshgrid(powerplot, freq[0])
#Y = np.concatenate((freq, freq[-1][:,None].T))
#Y = np.transpose(Y)
#pl.xlim(X.min(), X.max())
#pl.pcolormesh(X,Y,Z)
#pl.colorbar()
##pl.title('YIG FMR Spectrum, S11 Measurement')
##pl.xlabel('Magnetic Field(mT)')
#pl.ylabel('Frequency(GHz)')

fig = pl.figure()
gs = gridspec.GridSpec(1, 2)
fig.add_subplot(gs[0])
fig.add_subplot(gs[1])


if fit_S12 or fit_S11:
    xlist = np.zeros(len(real))
    kappa_a = np.zeros(len(real))
    kappa_a_err = np.zeros(len(real))
    Q_result = np.zeros(len(real))
    omega_c = np.zeros(len(real))
    omega_c_err = np.zeros(len(real))
    kappa_prod = np.zeros(len(real))
    kappa_prod_err = np.zeros(len(real))

for i in range(len(real))[0:]:
    if seperate_fitting_figure:
        fig = pl.figure()
        gs = gridspec.GridSpec(1, 2)
        fig.add_subplot(gs[0])
        fig.add_subplot(gs[1])
    
    fig.axes[1].plot(real[i],imag[i], label= 'current = %smA'%(currents[i]))
    fig.axes[0].plot(freq[i]/1e9,mag[i], label= 'current = %smA'%(currents[i]))
    



    

    freqs = freq
    datas = real[i] + 1j*imag[i]
    if fit_S12:
        params = lmfit.Parameters()
        params.add('kappa_prod', value= (np.max(np.abs(datas))*2e6)**2.001, min = 0)#,vary = False)
        params.add('omega_c', value=freqs[i][np.argmax(np.abs(datas))]*1.000,min = freqs[i][np.argmax(np.abs(datas))]*0.9, max = freqs[i][np.argmax(np.abs(datas))] * 1.1)#,vary = False)
        params.add('kappa_a', value=2e6, min = 0)#, max = 4e6)#,vary = False)
        if np.max(np.abs(datas)) < limit_for_off:
            params.add('roff',value = 0)#,vary = False)
            params.add('ioff',value = 0)#, vary = False)
        params.add('phi',value = -1, max = np.pi, min = -np.pi)#,vary = False)
                
    #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
        result = lmfit.minimize(S21, params, args=(freqs[i], datas))
        lmfit.report_fit(result.params)
        print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
        fitdata = np.sqrt(result.params['kappa_prod'].value)/(-1j*(freqs[i]-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )
        if np.max(np.abs(datas)) < limit_for_off:
            fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
        fitdata = fitdata * np.exp(1j*result.params['phi'].value)
        fitdatadB = 20*np.log10(np.abs(fitdata))
    #    ampdata = 20*np.log10(np.sqrt(realdata[0,:]**2 + imagdata[0,:]**2))
    if fit_S11:
        params = lmfit.Parameters()
        params.add('kappa_1', value=2.1305e+05)
        params.add('omega_c', value=freqs[i][np.argmin(np.abs(datas))]*1.0001)
        params.add('kappa_a', value=3.0022e+06)
        params.add('A', value=1)
                
    #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
        result = lmfit.minimize(S11, params, args=(freqs[i], abs(datas)))
#        lmfit.report_fit(result.params)
        print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
        print ('coupling Q: ',result.params['omega_c'].value/result.params['kappa_1'].value)
        fitdata = (-1 - result.params['kappa_1'].value / (-1j*(freqs[i]-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value
        fitdatadB = 20*np.log10(np.abs(fitdata))


    #    fig.axes[0].set_title(figname)
#    pl.suptitle(figname)
    if fit_S12 or fit_S11:
        fig.axes[0].plot(freqs[i]/float(1e9), fitdatadB,'--' )
        fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
        xlist[i] = currents[i]
        kappa_a[i] = result.params['kappa_a'].value
        kappa_a_err[i] = result.params['kappa_a'].stderr
        Q_result[i] =result.params['omega_c'].value /result.params['kappa_a'].value
        omega_c[i] = result.params['omega_c'].value
        omega_c_err[i] = result.params['omega_c'].stderr
        if fit_S12:   
            kappa_prod[i] = result.params['kappa_prod'].value
            kappa_prod_err[i] = result.params['kappa_prod'].stderr
#    pl.xlabel('freq(GHz)')

    fig.axes[1].set_aspect('equal', 'box')
    
    pl.legend()



#pl.figure()
#pl.errorbar(xlist, kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa_tot')
#pl.xlabel('drive power (dbm)')
#pl.ylabel('linewidth(MHz)')
#pl.legend(loc='upper right')
##pl.savefig(save_filepath + 'kappas.png')
#pl.figure()
#pl.errorbar(xlist, kappa_prod, yerr = kappa_prod_err, fmt ='o', label='kappa_prod')
#pl.xlabel('drive power (dBm)')
#pl.legend(loc='upper right')
#pl.figure()
#pl.scatter(xlist, Q_result, label='total Q')
##    pl.xlabel('field(T)')
##    pl.xlabel('different measurement')
#pl.xlabel('drive power (dBm)')
#pl.ylabel('Q')
#pl.legend(loc='upper right')
##pl.savefig(save_filepath + 'Qs.png')

field = xlist
if xlabel == 'different measurements':
    field = range(len(field))
#lin_power[0] = 0
field_plot = np.concatenate((field, np.zeros(1) + field[2] - field[1] + field[-1]))

pl.figure()
freq0, X_lin= np.meshgrid(freq[0], field_plot) 
Z = 10*np.log10(real**2 + imag**2)
Y = np.concatenate((freq, freq[-1][:,None].T))

pl.xlim(X_lin.min(), X_lin.max())
for i in range(len(xlist)-1):
    z1 = Z[i]
    z1 = z1[:,None].T
    z2 = Z[i]
    z2 = z2[:,None].T
    z = np.concatenate([z1,z2])
    z = np.transpose(z)
    x = np.zeros((len(Y[i]),2))
    x[:,0] = X_lin[i]
    x[:,1] = X_lin[i+1]
    y = np.zeros((2,len(Y[i])))
    y[0] = y[1] = freqs[i]
    y = np.transpose(y)
    pl.pcolormesh(x, y, z,vmax=np.max((np.max(Z),-200)),vmin = np.max((-200,np.min(Z))))

pl.colorbar()
#pl.title('YIG FMR Spectrum, S11 Measurement')
#pl.xlabel('Magnetic Field(mT)')
pl.xlabel(xlabel)
pl.ylabel('Frequency(GHz)')

pl.figure()
pl.scatter(field , omega_c/1e9, label='frequency')
#    pl.xlabel('field(T)')
#    pl.xlabel('different measurement')
n=18
#m,b = np.polyfit(field [1:n],omega_c[1:n]/1e9,1)
#print 'slope for frequency:', m
#pl.plot(field , field *m + b,label = 'frequencu(GHz) = %s * current(mA) + %s'%(m,b))
pl.xlabel(xlabel)
pl.ylabel('frequency(GHz)')
pl.legend(loc='upper right')

pl.figure()
pl.scatter(field , Q_result, label='total Q')
#    pl.xlabel('field(T)')
#    pl.xlabel('different measurement')
pl.xlabel(xlabel)
pl.ylabel('Q')
pl.legend(loc='upper right')


pl.figure()
pl.errorbar(field , kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa_tot')
n=5
#m,b = np.polyfit(field [0:n],kappa_a[0:n]/1e6,1)
#pl.plot(field , field *m + b, label = 'kappa(MHz) = %s * current(mW) + %s'%(m,b))
#print 'slope for kappa:', m
pl.ylim(0,5)
pl.xlabel(xlabel)
pl.ylabel('linewidth(MHz)')
pl.legend(loc='upper right')
print 'ave = ',np.average(kappa_a/1000000), 'MHz' 
print 'err = ', np.std(kappa_a/1000000)/len(kappa_a), 'MHz'


pl.figure()
pl.errorbar(field , kappa_prod, yerr = kappa_prod_err, fmt ='o', label='kappa_prod')
pl.xlabel(xlabel)
pl.legend(loc='upper right')