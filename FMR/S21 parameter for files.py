# -*- coding: utf-8 -*-
"""
Created on Tue Apr 03 10:43:08 2018

@author: Wang_Lab
"""

import lmfit

import numpy as np
import matplotlib.pyplot as pl
import glob

def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
    est = -est
    
    return np.abs(y)-np.abs(est)
    #np.concatenate([y.real - est.real, y.imag - est.imag])
    #y.real - est.real
    #np.abs(y)-np.abs(est)
    #resid.view(np.float)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
for filename in glob.glob('C:\qrlab\FMR\power_sweep\*.txt'):
# Read the array from file

    new_data = np.loadtxt(r'C:\qrlab\FMR\power_sweep\%s.txt'%(filename),delimiter=",")# while using this fitting, make sure that your peak is exactly at the center
    new_data = np.transpose(new_data)
    x = new_data[0] 
    y = new_data[1] 
    phase = new_data[2]
    #print(min(x), max(x))
    #x = x.astype(float)
    #print(min(x), max(x))
    x = x * 1000000000
    
    
    ##plotting s21^2 to get the linewidth of the cavity
    #y = np.power(10,y/10.0)
    #pl.plot(x, y)
    
    y = np.power(10,y/20.0)
    pl.figure()
    pl.suptitle('fitting for %s'%(filename))
    pl.subplot(211)
    pl.plot(x, y)
    pl.ylabel('intensity')
    
    if 0: #if the phase reaches -180
        index_min = np.argmin(phase)
        phase[index_min + 1 : ] = phase[index_min + 1 : ] - 360
    
    phase_ave = np.average(phase)
    phase = phase - phase_ave
    phase = phase * 2 * np.pi /float(360)   
    y = y * np.exp(-1j*phase)
    
    #print abs(1+1j)
    
     
    params = lmfit.Parameters()
    params.add('kappa_prod', value= 6.8e10, min = 0)
    params.add('omega_c', value=8.512e9)
    params.add('kappa_a', value=1e6, min = 0)
    
    
    result = lmfit.minimize(S21, params, args=(x, y))
    
    lmfit.report_fit(result.params)
    y1 = np.sqrt(result.params['kappa_prod'].value)/(1j*(x-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )
    
    
    pl.plot(x, np.abs(y1),'--')
    pl.xlabel('frequency')
    pl.legend()
    
    pl.subplot(212)
    pl.plot(x, - phase)
    pl.plot(x, np.arctan(y1.imag/y1.real),'--')
    #pl.plot(x, np.arctan(est.imag/est.real),'--')
    pl.xlabel('frequency')
    pl.ylabel('phase')
    pl.legend()

    f= open('C:\qrlab\FMR\power_sweep\parameters_%s.txt'%(filename),'a')
    f.writelines('%s    %s\n'%(filename, result.params))
    f.close()
