# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 18:27:31 2019

@author: Wang_Lab
"""
import matplotlib
matplotlib.interactive(True)
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
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '0626cooldown_circualtor_VNA - Copy.hdf5'
#hdf5_name = '0612cooldown_FMR - Copy.hdf5'
date = '20200629'
time = '231307'
experiment = 'SingleTrace'
#experiment = 'SingleTraceNoAsync'

fit_S12 = False
fit_S11 = False
fit_S12_two_modes = False
fit_S12_two_modes_V2 = False
fit_S12_two_modes_V3= False
fit_S12_three_modes= True
fft = False
subtract = False
if subtract:
#    hdf5_name_s = '0531cooldown_FMR.hdf5'
    hdf5_name_s = hdf5_name
    date_s = '20190815'
    time_s = '161707'
    experiment_s = 'SingleTrace'
#    experiment_s = 'SingleTraceNoAsync'
def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est * np.exp(1j*params['phi'])
    
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    
    
def S11(params, x, y):

    est = (-1 - params['kappa_1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2))*params['A']
    return y - abs(est)

    
def S21_two_modes(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 + params['g']**2/(-1j *(x-params['omega_fmr'])-params['kappa_fmr']/2))
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est * np.exp(1j*params['phi'])
    
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    
    
def S21_two_modes_V2(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est * (-1 - params['kappa_1'] / (-1j*(x-params['omega_fmr'])-params['kappa_fmr']/2))
    est = est * np.exp(1j*params['phi'])

    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    #np.abs(y) - np.abs(est)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
def S21_two_modes_V3(params, x, y):
    est = np.sqrt(params['kappa_prod1'])/(-1j*(x-params['omega_c'])-(params['kappa_a1'])/2.0 )* np.exp(1j*params['phi1'])
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est + np.sqrt(params['kappa_prod2'])/(-1j*(x-params['omega_c2'])-(params['kappa_a2'])/2.0 ) * np.exp(1j*(params['phi21']+params['phi1']))

    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)  
    
def S21_three_modes(params, x, y):
    est = np.sqrt(params['kappa_prod1'])/(-1j*(x-params['omega_c'])-(params['kappa_a1'])/2.0 )* np.exp(1j*params['phi1'])
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est + np.sqrt(params['kappa_prod2'])/(-1j*(x-params['omega_c2'])-(params['kappa_a2'])/2.0 ) * np.exp(1j*(params['phi21']+params['phi1']))
    est = est + np.sqrt(params['kappa_prod3'])/(-1j*(x-params['omega_c3'])-(params['kappa_a3'])/2.0 ) * np.exp(1j*(params['phi31']+params['phi1']))

    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2) 
    
limit_for_off =1

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

real = exp['real'].value
imag = exp['imaginary'].value
f.close()
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
    real = real - real_s
    imag = imag - imag_s
    f_s.close()
'''Conversion factor from Yoko current in mA to actual magnetic field in mT'''
#if current.any() < 0.5:
#    field = current*529.37 + 0.49
#else:
#    field = -268.93 * (current)**2 + 839.69*current - 88.67

'''Plot'''




#mag = 10*np.log10(real**2 + imag**2)
datas = real + 1j*imag
#datas = datas * np.exp(1j *10e-9 * freq)
mag = np.abs(datas)

pl.figure()
pl.plot(freq[0]/1e9, np.angle(datas[0]))
fig = pl.figure()
gs = gridspec.GridSpec(1, 2)
fig.add_subplot(gs[0])
fig.add_subplot(gs[1])



fig.axes[1].plot(np.real(datas[0]), np.imag(datas[0]))
fig.axes[0].plot(freq[0]/1e9,mag[0])






freqs = freq[0]

#
#freqs = freqs[0:1500]
#datas = datas[0][0:1500]


if fit_S12:
    params = lmfit.Parameters()
    params.add('kappa_prod', value= (np.max(np.abs(datas))*0.5e6)**2.001, min = 0)#,vary = False)
    params.add('omega_c', value=freqs[np.argmax(np.abs(datas))]*1.0001,min = freqs[np.argmax(np.abs(datas))]*0.9998, max = freqs[np.argmax(np.abs(datas))] * 1.0002)#,vary = False)
    params.add('kappa_a', value=1e6, min = 0)#, max = 4e6)#,vary = False)
    if np.max(np.abs(datas)) < limit_for_off:
        params.add('roff',value = 1e-5)#,vary = False)
        params.add('ioff',value = 1e-5)#, vary = False)
    params.add('phi',value = -1, max = np.pi, min = -np.pi)#,vary = False)
            
#    datas = realdata[0,:]+ 1j*imagdata[0,:]    
    result = lmfit.minimize(S21, params, args=(freqs, datas))
    lmfit.report_fit(result.params)
    print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
    fitdata = np.sqrt(result.params['kappa_prod'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )
    if np.max(np.abs(datas)) < limit_for_off:
        fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
    fitdata = fitdata * np.exp(1j*result.params['phi'].value)
    fitdatadB = 20*np.log10(np.abs(fitdata))
#    ampdata = 20*np.log10(np.sqrt(realdata[0,:]**2 + imagdata[0,:]**2))
if fit_S11:
    params = lmfit.Parameters()
    params.add('kappa_1', value=2.1305e+05)
    params.add('omega_c', value=freqs[np.argmin(np.abs(datas))]*1.0001)
    params.add('kappa_a', value=3.0022e+06)
    params.add('A', value=1)
            
#    datas = realdata[0,:]+ 1j*imagdata[0,:]    
    result = lmfit.minimize(S11, params, args=(freqs, abs(datas)))
    lmfit.report_fit(result.params)
    print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
    print ('coupling Q: ',result.params['omega_c'].value/result.params['kappa_1'].value)
    fitdata = (-1 - result.params['kappa_1'].value / (-1j*(freqs-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value
    fitdatadB = 20*np.log10(np.abs(fitdata))

if fit_S12_two_modes:
    params = lmfit.Parameters()
    params.add('kappa_prod', value= 10e12, min = 0)#,vary = False)
    params.add('omega_c', value=10.934e9)#,vary = False)
    params.add('kappa_a', value=1e6, min = 0)#, max = 4e6)#,vary = False)
    if np.max(np.abs(datas)) < limit_for_off:
        params.add('roff',value = 0)#,vary = False)
        params.add('ioff',value = 0)#, vary = False)
    params.add('phi',value = 1.5, max = np.pi, min = -np.pi)#,vary = False)
            

    params.add('g', value= 2e6, min = 0)#,vary = False)
    params.add('omega_fmr', value=10.936e9)#,vary = False)
    params.add('kappa_fmr', value=1e6, min = 0)
    result = lmfit.minimize(S21_two_modes, params, args=(freqs, abs(datas)))
    lmfit.report_fit(result.params)
    fitdata = np.sqrt(result.params['kappa_prod'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 + result.params['g'].value**2/(-1j *(freqs-result.params['omega_fmr'].value)-result.params['kappa_fmr'].value/2))+ result.params['roff'].value + 1j*result.params['ioff'].value
    fitdata = fitdata * np.exp(1j*result.params['phi'].value)
    fitdatadB = 20*np.log10(np.abs(fitdata))
    
if fit_S12_two_modes_V2:
    params = lmfit.Parameters()
    params.add('kappa_prod', value= 10e9, min = 0)#,vary = False)
    params.add('omega_c', value=10.932e9)#,vary = False)
    params.add('kappa_a', value=1e6, min = 0, max = 4e6)#,vary = False)
    if np.max(np.abs(datas)) < limit_for_off:
        params.add('roff',value = 0)#,vary = False)
        params.add('ioff',value = 0)#, vary = False)
    params.add('phi',value = 1.7, max = np.pi, min = -np.pi,vary = False)
            

    params.add('kappa_1', value= 3e6, min = 0)#,vary = False)
    params.add('omega_fmr', value=10.934e9)#,vary = False)
    params.add('kappa_fmr', value=2e6, min = 0)#,vary = False)
    result = lmfit.minimize(S21_two_modes_V2, params, args=(freqs, abs(datas)))
    lmfit.report_fit(result.params)
    fitdata = np.sqrt(result.params['kappa_prod'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )
    if np.max(np.abs(datas)) < limit_for_off:
        fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
    fitdata = fitdata * (-1 - result.params['kappa_1'].value / (-1j*(freqs-result.params['omega_fmr'].value)-result.params['kappa_fmr'].value/2))
    fitdata = fitdata * np.exp(1j*result.params['phi'].value)
    fitdatadB = 20*np.log10(np.abs(fitdata))
#    fig.axes[0].set_title(figname)
#    pl.suptitle(figname)

if fit_S12_two_modes_V3:
    params = lmfit.Parameters()
    params.add('kappa_prod1', value=3e8, min = 0)#,vary = False)
    params.add('omega_c', value=10.805e9)#,vary = False)
    params.add('kappa_a1', value=2.5e6, min = 0)#,vary = False)
    if np.max(np.abs(datas)) < limit_for_off:
        params.add('roff',value =(datas[0][0].real+ datas[0][-1].real)/2)#,vary = False)
        params.add('ioff',value = (datas[0][0].imag+ datas[0][-1].imag)/2)#, vary = False)
    params.add('phi1',value =-0.5, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
        

    params.add('kappa_prod2', value= 1e10, min = 0)#,vary = False)
    params.add('omega_c2', value=10.81e9)#,vary = False)
    params.add('kappa_a2', value = 200e6, min = 0)#,vary = False)
    params.add('phi21',value =2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
    
    
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
    result = lmfit.minimize(S21_two_modes_V3, params, args=(freqs, datas))
    lmfit.report_fit(result.params)
    fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a1'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
    if np.max(np.abs(datas)) < limit_for_off:
        fitdata1 = fitdata1 + result.params['roff'].value + 1j*result.params['ioff'].value
    fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
    fitdata = fitdata1 + fitdata2
    fitdatadB = 20*np.log10(np.abs(fitdata))
    
    fig.axes[0].plot(freqs/float(1e9), np.abs(fitdata),'--' )
    fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
    
if fit_S12_three_modes:
    params = lmfit.Parameters()
    params.add('kappa_prod1', value=2e9, min = 0)#,vary = False)
    params.add('omega_c', value=10.805e9)#,vary = False)
    params.add('kappa_a1', value=1e6, min = 0)#,vary = False)
    if np.max(np.abs(datas)) < limit_for_off:
        params.add('roff',value =(datas[0][0].real+ datas[0][-1].real)/2)#,vary = False)
        params.add('ioff',value = (datas[0][0].imag+ datas[0][-1].imag)/2)#, vary = False)
    params.add('phi1',value =3, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
        

    params.add('kappa_prod2', value= 1e11, min = 0)#,vary = False)
    params.add('omega_c2', value=10.815e9)#,vary = False)
    params.add('kappa_a2', value = 2e7, min = 0)#,vary = False)
    params.add('phi21',value =2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)

    params.add('kappa_prod3', value= 1e11, min = 0)#,vary = False)
    params.add('omega_c3', value=10.78e9)#,vary = False)
    params.add('kappa_a3', value = 50e6, min = 0)#,vary = False)
    params.add('phi31',value =-2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
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
    fitdatadB = 20*np.log10(np.abs(fitdata))
    
    fig.axes[0].plot(freqs/float(1e9), np.abs(fitdata),'--' )
    fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
if fit_S12 or fit_S11 or fit_S12_two_modes or fit_S12_two_modes_V2 :
    fig.axes[0].plot(freqs/float(1e9), fitdatadB,'--' )
    fig.axes[1].plot(fitdata.real,fitdata.imag, '--', label = 'total Q = %s\n kappa_tot = %sMHz'%(result.params['omega_c'].value/result.params['kappa_a'].value, result.params['kappa_a'].value/1e6))

#    pl.xlabel('freq(GHz)')

fig.axes[1].set_aspect('equal', 'box')
    
pl.legend()


if fft:
    FFT = np.fft.fft(datas[0])
    FFT = FFT[0:len(FFT)/2]
    pl.figure()
    pl.loglog(np.abs(FFT)**2,'.')
    pl.show()
    
    
