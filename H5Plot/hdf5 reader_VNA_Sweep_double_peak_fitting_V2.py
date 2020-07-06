# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 16:58:09 2019

@author: WangLab
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 19:10:45 2019

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
hdf5_name = '0612cooldown_FMR.hdf5'
#hdf5_name = '0612cooldown_FMR - Copy (2).hdf5'
date = '20190618'
time = '154659'
experiment = 'Magnet_Sweep_VNA'

fit_S12 = True
fit_S11 = False

subtract = False
subtract_bg = False

if subtract:
#    hdf5_name_s = '0531cooldown_FMR.hdf5'
    hdf5_name_s = hdf5_name
    date_s = '20190617'
    time_s = '201654'
    experiment_s = 'SingleTrace'

def S21(params, x, y):
    est = 0.0*y[:]
    for i in fitting_range:
        est[i] = np.sqrt(params['kappa_prod_%s'%(i)])/(-1j*(x-params['omega_c_%s'%(i)])-(params['kappa_a_%s'%(i)])/2.0 + params['g_%s'%(i)]**2/(-1j *(x-params['omega_fmr_%s'%(i)])-params['kappa_fmr_%s'%(i)]/2))
        est[i] = est[i] + params['roff_%s'%(i)] + 1j*params['ioff_%s'%(i)]
        est[i] = est[i] * np.exp(1j*params['phi_%s'%(i)])
    
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    
    



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
#current = exp['currents'].value
#powers = exp['powers'].value
powers = exp['fields'].value
real = exp['realS21'].value
imag = exp['imaginaryS21'].value

if subtract:
    f_s = h5.File(filepath + hdf5_name_s, 'r')
    exp_s = f_s['/' + date_s + '/' + time_s + '_' + experiment_s]
    y_keys_s = exp_s.keys()
    #print(y_keys)
    
    #y_keys.remove(x_key)
    #y_keys.remove(x2_key)
    freq_s = exp_s['freqs'].value

    real_s = exp_s['real'].value
    imag_s = exp_s['imaginary'].value

'''Conversion factor from Yoko current in mA to actual magnetic field in mT'''
#if current.any() < 0.5:
#    field = current*529.37 + 0.49
#else:
#    field = -268.93 * (current)**2 + 839.69*current - 88.67

'''Plot'''


if subtract:
    for i in range(len(real)):
        real[i] = real[i] - real_s
        imag[i] = imag[i] - imag_s


if subtract_bg:
    for i in range(len(real)):
        real[i] = real[i] - background[0].real
        imag[i] = imag[i] - background[0].imag   
pl.figure()
figname = ''
powerplot = np.concatenate((powers, np.zeros(1) + powers[1]-powers[0] + powers[-1]))
mag = 10*np.log10(real**2 + imag**2)
Z = np.transpose(mag)
#X,Y = np.meshgrid(field, freq)
X,Y = np.meshgrid(powerplot, freq)
pl.xlim(X.min(), X.max())
pl.pcolormesh(X,Y,Z)
pl.colorbar()
#pl.title('YIG FMR Spectrum, S11 Measurement')
#pl.xlabel('Magnetic Field(mT)')
pl.ylabel('Frequency(GHz)')


datas = real +1j*imag

datas = np.transpose(datas)[30:]
datas = np.transpose(datas)

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
    kappa_fmr = np.zeros(len(real))
    kappa_fmr_err = np.zeros(len(real))
fitting_range = range(len(real))
params = lmfit.Parameters()
omega_fmri = np.zeros(len(real))
omega_ci = np.zeros(len(real))
for i in fitting_range:
    print powers[i]
    fig.axes[1].plot(real[i],imag[i], label= 'power = %sdB'%(powers[i]))
    fig.axes[0].plot(freq/1e9,mag[i], label= 'power = %sdB'%(powers[i]))
    omega_fmri[i] = 0.99*28.025*(powers[i]*1000+178*1.2*(0.444444-0.333333))/1000+0.495 - 1*(powers[i]-0.2678)
    omega_ci[i] = 8.599e9 + 1e9*(powers[i]-0.2678)
    omega_fmri[i] = omega_fmri[i] *1e9



    

    freqs = freq[30:]
#    datas = real[i] + 1j*imag[i]
#
#    freqs = freq[30:]
#    datas = datas[30:]
    if fit_S12:
        
#        params = lmfit.Parameters()
        params.add('kappa_prod_%s'%(i), value= 1.8e10, min = 0)#,vary = False)
        params.add('omega_c_%s'%(i), value=omega_ci[i])#,vary = False)
        params.add('kappa_a_%s'%(i), value=1.56e6, min = 0)#, max = 4e6)#,vary = False)
        if np.max(np.abs(datas)) < limit_for_off:
            params.add('roff_%s'%(i),value = 0)#,vary = False)
            params.add('ioff_%s'%(i),value = 0)#, vary = False)
        params.add('phi_%s'%(i),value = 1.5, max = np.pi, min = -np.pi)#,vary = False)
                

        params.add('g_%s'%(i), value= 3.16e6, min = 0)#,vary = False)
        params.add('omega_fmr_%s'%(i), value=omega_fmri[i])#,vary = False)
        params.add('kappa_fmr_%s'%(i), value=2e6, min = 0)

    #    params.add('kappa_fmr', value= 2e6, min = 0)
    #    params.add('omega_fmr', value=omega_fmr)
    #    params.add('g', value=2e7, min = 0)
for i in fitting_range[1:]:
#    params['kappa_prod_%s'%(i)].expr = 'kappa_prod_%s'%(fitting_range[0])   
#    params['omega_c_%s'%(i)].expr = 'omega_c_%s'%(fitting_range[0])
    params['kappa_a_%s'%(i)].expr = 'kappa_a_%s'%(fitting_range[0])
    params['roff_%s'%(i)].expr = 'roff_%s'%(fitting_range[0])
    params['ioff_%s'%(i)].expr = 'ioff_%s'%(fitting_range[0])
    params['phi_%s'%(i)].expr = 'phi_%s'%(fitting_range[0])
    params['g_%s'%(i)].expr = 'g_%s'%(fitting_range[0])
#    params['kappa_fmr_%s'%(i)].expr = 'kappa_fmr_%s'%(fitting_range[0])


    
result = lmfit.minimize(S21, params, args=(freqs,datas))
    
lmfit.report_fit(result.params)
fitdata = 0.0*datas[:]

for i in fitting_range:
    
    fitdata[i] = np.sqrt(result.params['kappa_prod_%s'%(i)].value)/(-1j*(freqs-result.params['omega_c_%s'%(i)].value)-(result.params['kappa_a_%s'%(i)].value)/2.0 + result.params['g_%s'%(i)].value**2/(-1j *(freqs-result.params['omega_fmr_%s'%(i)].value)-result.params['kappa_fmr_%s'%(i)].value/2) )
    fitdata[i] = fitdata[i] + result.params['roff_%s'%(i)].value + 1j*result.params['ioff_%s'%(i)].value
    fitdata[i] = fitdata[i] * np.exp(1j*result.params['phi_%s'%(i)].value)
    
fitdatadB = 20*np.log10(np.abs(fitdata))
for i in fitting_range:
    fig.axes[0].plot(freqs/float(1e9), fitdatadB[i],'--' )
    fig.axes[1].plot(fitdata[i].real,fitdata[i].imag, '--')
    
#    
#for 
#        xlist[i] = powers[i]
#        kappa_a[i] = result.params['kappa_a'].value
#        kappa_a_err[i] = result.params['kappa_a'].stderr
#        kappa_fmr[i] = result.params['kappa_fmr'].value
#        kappa_fmr_err[i] = result.params['kappa_fmr'].stderr
#        Q_result[i] =result.params['omega_c'].value /result.params['kappa_a'].value
#        omega_c[i] = result.params['omega_c'].value
#        omega_c_err[i] = result.params['omega_c'].stderr
#        if fit_S12:   
#            kappa_prod[i] = result.params['kappa_prod'].value
#            kappa_prod_err[i] = result.params['kappa_prod'].stderr
##    pl.xlabel('freq(GHz)')
#
#fig.axes[1].set_aspect('equal', 'box')
#    
#pl.legend()
#pl.figure()
#pl.errorbar(xlist, kappa_fmr/1000000, yerr = kappa_fmr_err/1000000, fmt ='o', label='kappa_fmr')
##pl.xlabel('drive power (dbm)')
##pl.ylabel('linewidth(MHz)')
##pl.legend(loc='upper right')
##
##pl.figure()
#pl.errorbar(xlist, kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa_cavity')
##pl.xlabel('drive power (dbm)')
#pl.ylabel('linewidth(MHz)')
#pl.legend(loc='upper right')