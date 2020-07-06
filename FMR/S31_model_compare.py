# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 21:23:20 2020

@author: Wang_Lab
"""
import os
import time
import lmfit 
import numpy as np
import matplotlib.pyplot as plt
import cmath


import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from matplotlib import gridspec


def S21_two_modes_V3(params, x, y):
    est = np.sqrt(params['kappa_prod1'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )* np.exp(1j*params['phi1'])
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est + np.sqrt(params['kappa_prod2'])/(-1j*(x-params['omega_c2'])-(params['kappa_a2'])/2.0 ) * np.exp(1j*(params['phi21']+params['phi1']))

    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    #np.abs(y) - np.abs(est)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
limit_for_off = 0.1


def S31(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
    A=gam1/2-1j*(w-w1)
    B=gam2/2-1j*(w-w2)
    C=gam3/2-1j*(w-w3)
    D=-1j*(w-w4)
    s31= gam3*gam1*abs((B*D*j1-B*delta*j2+2*j1*j2**2)/(B*D*j1**2+B*C*j2**2+4*j1**2*j2**2+A*(B*(C*D+delta**2)+D*j1**2+C*j2**2)))**2
    return s31
def S31_phase(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
    A=gam1/2-1j*(w-w1)
    B=gam2/2-1j*(w-w2)
    C=gam3/2-1j*(w-w3)
    D=-1j*(w-w4)
    s31_raw = 1j*(B*D*j1-B*delta*j2+2*j1*j2**2)/(B*D*j1**2+B*C*j2**2+4*j1**2*j2**2+A*(B*(C*D+delta**2)+D*j1**2+C*j2**2))
    s31_phase = []
    for i in range(len(w)):
        s31_phase.append(cmath.phase(s31_raw[i]))
    return s31_phase
w=np.linspace(10.7,10.725,10000)
delta = .6
j2=.019
j1=.03
gam3=.894
w1=10.7108
w2=10.7116
w3=10.619
w4=11.4642
gam1=.0016
gam2=.00076

deltalist = np.linspace(0,1,21)
fields = deltalist
freqs = w*1e9
xlist = np.zeros(len(fields))
kappa_a = np.zeros(len(fields))
kappa_a_err = np.zeros(len(fields))
Q_result = np.zeros(len(fields))
omega_c = np.zeros(len(fields))
omega_c_err = np.zeros(len(fields))
kappa_prod = np.zeros(len(fields))
kappa_prod_err = np.zeros(len(fields))

kappa_a2 = np.zeros(len(fields))
kappa_a2_err = np.zeros(len(fields))
omega_c2 = np.zeros(len(fields))
omega_c2_err = np.zeros(len(fields))
kappa_prod2 = np.zeros(len(fields))
kappa_prod2_err = np.zeros(len(fields))
phi21 = np.zeros(len(fields))
phi21_err = np.zeros(len(fields))
for itime, delta in enumerate(deltalist):
    
    S31_data=(S31(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w))
    S31_phase_data=(S31_phase(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w))
    # S31_data = []
    # S31_phase_data = []
    # for i in range(len(w4)):
    #     S31_data.append(S31(gam1,gam2,gam3,w1,w2,w3,w4[i],j1,j2,delta,w))
    #     S31_phase_data.append(S31(gam1,gam2,gam3,w1,w2,w3,w4[i],j1,j2,delta,w))
    datas = S31_data*np.cos(S31_phase_data) - 1j * S31_data*np.sin(S31_phase_data)
#    
#    plt.figure()
#    plt.plot(w,S31_phase_data)
#    plt.title('phase')
#    plt.figure()
#    plt.plot(w,S31_data)
#    plt.title('magnitude')
    fig = pl.figure()
    gs = gridspec.GridSpec(1, 2)
    fig.add_subplot(gs[0])
    fig.add_subplot(gs[1])
    fig.axes[1].plot(np.real(datas),np.imag(datas), label= 'delta = %s'%(delta))
    fig.axes[0].plot(freqs/1e9,np.abs(datas), label= 'delta = %s'%(delta))
    params = lmfit.Parameters()
    params.add('kappa_prod1', value=6e11, min = 0)#,vary = False)
    params.add('omega_c', value=10.71e9)#,vary = False)
    params.add('kappa_a', value=3e6, min = 0)#,vary = False)
    if np.max(np.abs(datas)) < limit_for_off:
        params.add('roff',value =(datas[0].real+ datas[-1].real)/2)#,vary = False)
        params.add('ioff',value = (datas[0].imag+ datas[-1].imag)/2)#, vary = False)
    params.add('phi1',value =1, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
            

    params.add('kappa_prod2', value= 1e11, min = 0)#,vary = False)
    params.add('omega_c2', value=10.713e9)#,vary = False)
    params.add('kappa_a2', value=2e6, min = 0)#,vary = False)
    params.add('phi21',value =1.5, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
    

    result = lmfit.minimize(S21_two_modes_V3, params, args=(freqs, datas))
    lmfit.report_fit(result.params)
    fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
    if np.max(np.abs(datas)) < limit_for_off:
        fitdata1 = fitdata1 + result.params['roff'].value + 1j*result.params['ioff'].value
    fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
    fitdata = fitdata1 + fitdata2
    fitdatadB = 20*np.log10(np.abs(fitdata))
    
    fig.axes[0].plot(freqs/float(1e9), np.abs(fitdata),'--' )
    fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
#    pl.close()
    xlist[itime] = fields[itime]
    kappa_a[itime] = result.params['kappa_a'].value
    kappa_a_err[itime] = result.params['kappa_a'].stderr
    Q_result[itime] =result.params['omega_c'].value /result.params['kappa_a'].value
    omega_c[itime] = result.params['omega_c'].value
    omega_c_err[itime] = result.params['omega_c'].stderr

    kappa_prod[itime] = result.params['kappa_prod1'].value
    kappa_prod_err[itime] = result.params['kappa_prod1'].stderr
    kappa_prod2[itime] = result.params['kappa_prod2'].value
    kappa_prod2_err[itime] = result.params['kappa_prod2'].stderr
    kappa_a2[itime] = result.params['kappa_a2'].value
    kappa_a2_err[itime] = result.params['kappa_a2'].stderr
    omega_c2[itime] = result.params['omega_c2'].value
    omega_c2_err[itime] = result.params['omega_c2'].stderr
    phi21[itime] = result.params['phi21'].value
    phi21_err[itime] = result.params['phi21'].stderr
    
    

pl.figure()
pl.errorbar(xlist, omega_c/1e9, yerr =omega_c_err/1e9, fmt ='o', label='frequency')
pl.errorbar(xlist, omega_c2/1e9, yerr =omega_c2_err/1e9, fmt ='o', label='frequency')

pl.ylabel('frequency(GHz)')
pl.legend(loc='upper right')




pl.figure()
pl.errorbar(xlist, kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa_tot')
pl.errorbar(xlist, kappa_a2/1000000, yerr = kappa_a2_err/1000000, fmt ='o')
pl.ylabel('linewidth(MHz)')
pl.legend(loc='upper right')

#
pl.figure()
pl.errorbar(xlist, kappa_prod, yerr = kappa_prod_err, fmt ='o', label='kappa_prod')
pl.errorbar(xlist, kappa_prod2, yerr = kappa_prod2_err, fmt ='o')
pl.legend(loc='upper right')    
    
    
pl.figure()
pl.errorbar(xlist,phi21, yerr = phi21_err, fmt ='o', label='phi21')
pl.legend(loc='upper right') 