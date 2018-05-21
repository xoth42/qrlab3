# -*- coding: utf-8 -*-
"""
Created on Tue Apr 03 10:43:08 2018

@author: Wang_Lab
"""

import lmfit
<<<<<<< HEAD
import re
=======

>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
import numpy as np
import matplotlib.pyplot as pl
import glob

<<<<<<< HEAD
pl.figure()
=======
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
    est = -est
    
    return np.abs(y)-np.abs(est)
    #np.concatenate([y.real - est.real, y.imag - est.imag])
    #y.real - est.real
    #np.abs(y)-np.abs(est)
    #resid.view(np.float)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
<<<<<<< HEAD
filelist = glob.glob(r'C:\Users\Wang_Lab\Documents\yingying\FMR\220 mode RT\*.txt')
pl.title('temperature dependence')
line=np.empty(len(filelist))
temp=np.empty(len(filelist))
#line1=np.empty(len(filelist))
#temp1=np.empty(len(filelist))
err=np.empty(len(filelist))
i=0
for filename in filelist:
# Read the array from file
    print filename
    new_data = np.loadtxt(filename,delimiter=",")
=======
for filename in glob.glob('C:\qrlab\FMR\power_sweep\*.txt'):
# Read the array from file

    new_data = np.loadtxt(r'C:\qrlab\FMR\power_sweep\%s.txt'%(filename),delimiter=",")# while using this fitting, make sure that your peak is exactly at the center
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
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
<<<<<<< HEAD
    
#==============================================================================
#     pl.figure()
#     pl.suptitle('fitting for %s'%(filename))
#     pl.subplot(211)
#     pl.plot(x, y)
#     pl.ylabel('intensity')
#     
#==============================================================================
#    if 0: #if the phase reaches -180
#        index_min = np.argmin(phase)
#        phase[index_min + 1 : ] = phase[index_min + 1 : ] - 360
#    
#    phase_ave = np.average(phase)
#    phase = phase - phase_ave
#    phase = phase * 2 * np.pi /float(360)   
=======
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
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
    y = y * np.exp(-1j*phase)
    
    #print abs(1+1j)
    
     
    params = lmfit.Parameters()
<<<<<<< HEAD
    params.add('kappa_prod', value= 3e9, min = 0)
    params.add('omega_c', value=8.54e9)
    params.add('kappa_a', value=2.2e6, min = 0)
    
    
    result = lmfit.minimize(S21, params, args=(x, y))

=======
    params.add('kappa_prod', value= 6.8e10, min = 0)
    params.add('omega_c', value=8.512e9)
    params.add('kappa_a', value=1e6, min = 0)
    
    
    result = lmfit.minimize(S21, params, args=(x, y))
    
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
    lmfit.report_fit(result.params)
    y1 = np.sqrt(result.params['kappa_prod'].value)/(1j*(x-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )
    
    
<<<<<<< HEAD
#==============================================================================
#     pl.plot(x, np.abs(y1),'--')
#     pl.xlabel('frequency')
#     pl.legend()
#     
#     pl.subplot(212)
#     pl.plot(x, - phase)
#     pl.plot(x, np.arctan(y1.imag/y1.real),'--')
#     #pl.plot(x, np.arctan(est.imag/est.real),'--')
#     pl.xlabel('frequency')
#     pl.ylabel('phase')
#     pl.legend()
#==============================================================================
    digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", filename)
    print digit
#    pl.errorbar(digit[2], result.params['kappa_a'].value/float(1000000),yerr=result.params['kappa_a'].stderr/float(1000000))
    temp[i] = digit[2]
    if temp[i] == 10:
        pl.figure()
        pl.suptitle('fitting for %s'%(filename))
        pl.plot(x, np.abs(y))
        pl.ylabel('intensity')
        lmfit.report_fit(result.params)
        pl.plot(x, np.abs(y1),'--')
        pl.xlabel('frequency')
        pl.legend()
    line[i] = result.params['kappa_a'].value/float(1000000)
    err[i]=result.params['kappa_a'].stderr/float(1000000)
    i=i+1
pl.figure()
pl.errorbar(temp,line,yerr=err,fmt='o')
pl.xlabel('power')
#pl.xlabel('T(mK)')
#pl.xscale('log')
pl.ylabel('linewidth(MHz)')
pl.legend()
h = 6.63
w = 8.08
k = 0.138

#==============================================================================
# for i in range(len(temp)):
#     if temp[i] <=1000:
#         temp1[i]=temp[i]
#         line1[i]=line[i]
#     else:
#         temp1[i]=0
#         line1[i]=0
# 
# np.delete(temp1,[0])
#==============================================================================


        
#==============================================================================
# def TLS_Fit(params,x,y):
#     est= params['gamma_0']*np.tanh((h*w)/(2*k*x))+params['gamma_m']
# #    est=(-params['gamma_0']*np.tanh((h*w)/(2*k*x)))+8
#     return np.abs(y)-np.abs(est)
# params = lmfit.Parameters()
# params.add('gamma_0',value=0.4)
# params.add('gamma_m',value=2)
# result = lmfit.minimize(TLS_Fit,params,args=(temp,line))
# lmfit.report_fit(result.params)
# fit = np.arange(int(np.amin(temp)),int(np.amax(temp)))
# linefit = result.params['gamma_0']*np.tanh((h*w)/(2*k*fit))+result.params['gamma_m']
# pl.plot(fit,linefit)
#==============================================================================
#==============================================================================
#     f= open('%s\parameters.txt'%(filename[0:52]),'a')
#     f.writelines('%s    %s\n'%(filename, result.params))
#     f.close()
#==============================================================================
=======
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
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
