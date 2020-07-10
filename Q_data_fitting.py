# -*- coding: utf-8 -*-
"""
Created on Wed Jul 03 16:48:03 2019

@author: WangLab
"""
from scipy.optimize import curve_fit
from scripts.single_cavity import VNA_single_trace_V2
import numpy as np
import lmfit
from lmfit import Parameters, Minimizer, report_fit
import matplotlib.pyplot as pl
e = np.exp([1])[0]
print(e)
def s21_theory_resid(params,x,data): #qi = internal Q, qc = coupling Q, w0 = resonant frequency,
#x = driving frequency, dw = effective frequency shift,w0t = complex resonant frequency to take losses into account
    qi = params['internal_Q']
    qc = params['coupling_Q']
    w0 = params['omega_0']
    dw = params['delta_omega']
    A = params['amplitude']
    P = params['phase']
    
    f = (qc + 1j*qc*qi*(2*(x-(w0+dw))/(w0+dw) + 2*dw/w0))/(qi+qc + 2*1j*qc*qi*(x-(w0+dw))/(w0+dw))*(A)*(e**(1j*P))
    res = np.abs(f-data)
    return(res)
# see Kurtis Lee Geerlings' thesis for more infromation on the fit
def s_21_func(x,qi,qc,w0,dw,A,P):
    f = (qc + 1j*qc*qi*(2*(x-(w0+dw))/(w0+dw) + 2*dw/w0))/(qi+qc + 2*1j*qc*qi*(x-(w0+dw))/(w0+dw))*(A)*(e**(1j*P))
    return (f)

freq_data = tuple(VNA.do_get_xaxis())
raw_data = VNA.do_get_data()
mag_data = 10**(raw_data[0]/20) 
phase_data = raw_data[1]   
    
    
params = Parameters()
params.add('internal_Q',value = 12000, vary = True)
params.add('coupling_Q', value = 100000, vary = True)
params.add('omega_0', value = freq_data[np.argmin(mag_data)], vary = True)
params.add('delta_omega', value = 0, vary = False)
params.add('amplitude', value = (mag_data[0]+mag_data[-1])/2, vary = False)
params.add('phase', value = (phase_data[0]+phase_data[-1])/2 , vary = False)

#phase = np.cos(raw_data[1]) + 1j*np.sin(raw_data[1])
#s21_data = mag_data * phase
s21_data = mag_data*np.cos(raw_data[1]*(2*np.pi/360)) + 1j*mag_data*np.sin(raw_data[1]*(2*np.pi/360))
s21_data_tuple = tuple(s21_data)

minner = Minimizer(s21_theory_resid,params,fcn_args=(freq_data,s21_data))
result = minner.minimize(method = 'leastsq')
#final = s21_data + result.residual
s21_theory = s_21_func(freq_data,result.params['internal_Q'],result.params['coupling_Q'],result.params['omega_0'],result.params['delta_omega'],result.params['amplitude'],result.params['phase'])
#Qinternal = fit_mag[3]
#Qcoupling = fit_mag[4]
#print('Qinternal =' + str(Qinternal) + ', Qcoupling =' + str(Qcoupling))
#fit = lmfit.leastsquares(s21,xdata,ydata)
print(report_fit(result))
pl.figure()
pl.plot(np.real(s21_data),np.imag(s21_data))
pl.plot(np.real(s21_theory),np.imag(s21_theory))
pl.show()

pl.figure()
pl.plot(freq_data,20*np.log10(mag_data))
pl.plot(freq_data,20*np.log10(np.abs(s21_theory)))
pl.show()