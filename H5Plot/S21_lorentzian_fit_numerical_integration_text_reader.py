# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 19:18:18 2021

@author: WangLab
"""

import os
import time
import lmfit 


import matplotlib
matplotlib.interactive(True)
import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from matplotlib import gridspec
import scipy.linalg as la
from scipy import integrate

limit_for_off = 1
def S21_two_modes_V3(params, x, y):
    est = np.sqrt(params['kappa_prod1'])/(-1j*(x-params['omega_c'])-(params['kappa_a1'])/2.0 )* np.exp(1j*params['phi1'])
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est + np.sqrt(params['kappa_prod2'])/(-1j*(x-params['omega_c2'])-(params['kappa_a2'])/2.0 ) * np.exp(1j*(params['phi21']+params['phi1']))

    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    #np.abs(y) - np.abs(est)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    

def S21_three_modes(params, x, y):
    est = np.sqrt(params['kappa_prod1'])/(-1j*(x-params['omega_c'])-(params['kappa_a1'])/2.0 )* np.exp(1j*params['phi1'])
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est + np.sqrt(params['kappa_prod2'])/(-1j*(x-params['omega_c2'])-(params['kappa_a2'])/2.0 ) * np.exp(1j*(params['phi21']+params['phi1']))
    est = est + np.sqrt(params['kappa_prod3'])/(-1j*(x-params['omega_c3'])-(params['kappa_a3'])/2.0 ) * np.exp(1j*(params['phi31']+params['phi1']))

    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)  


data_txt = np.loadtxt('C:\\Users\\WangLab\\Documents\\circulator results\\20210222_094030\\s21_results-.05to.05.txt')
fields = np.asarray([0,-.005,-.01,-.015,-.02,-.03,-.04,-.05,0,.005,.01,.02,.03,.04,.05])
pts_num = len(fields)
data_len = 1601
data_g = np.zeros((len(fields),data_len),dtype = complex)
data_e = np.zeros((len(fields),data_len), dtype = complex)
freqs = data_txt[0]*1e9
for i in range(pts_num):
    data_g[i] = data_txt[15+i] + 1j*data_txt[30+i]
    data_e[i] = data_txt[45+i] + 1j*data_txt[60+i]


two_modes = True
three_modes = False

final_plot = True

create_array = True

save_data = True

field_range = list(range(0,15))

model_data_len = 4001
freqs_model = np.linspace(10.78e9,10.83e9,model_data_len)
data_midg = np.zeros((len(fields),model_data_len))
data_mide = np.zeros((len(fields),model_data_len))

tf = 140

#if itime == True:
#    datas = np.zeros([len(fields),1601],dtype = complex)
if two_modes:
    if create_array == True:
        
#        datas = np.zeros([len(fields),1601],dtype = complex)
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
        
        xlist_e = np.zeros(len(fields))
        kappa_a_e = np.zeros(len(fields))
        kappa_a_err_e = np.zeros(len(fields))
        Q_result_e = np.zeros(len(fields))
        omega_c_e = np.zeros(len(fields))
        omega_c_err_e = np.zeros(len(fields))
        kappa_prod_e = np.zeros(len(fields))
        kappa_prod_err_e = np.zeros(len(fields))
        
        kappa_a2_e = np.zeros(len(fields))
        kappa_a2_err_e = np.zeros(len(fields))
        omega_c2_e = np.zeros(len(fields))
        omega_c2_err_e = np.zeros(len(fields))
        kappa_prod2_e = np.zeros(len(fields))
        kappa_prod2_err_e = np.zeros(len(fields))
        phi21_e = np.zeros(len(fields))
        phi21_err_e = np.zeros(len(fields))
if three_modes:
    if create_array == True:
        
#        datas = np.zeros([len(fields),1601],dtype = complex)
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
    
        kappa_a3 = np.zeros(len(fields))
        kappa_a3_err = np.zeros(len(fields))
        omega_c3 = np.zeros(len(fields))
        omega_c3_err = np.zeros(len(fields))
        kappa_prod3 = np.zeros(len(fields))
        kappa_prod3_err = np.zeros(len(fields))
        phi31 = np.zeros(len(fields))
        phi31_err = np.zeros(len(fields))
        
        xlist_e = np.zeros(len(fields))
        kappa_a_e = np.zeros(len(fields))
        kappa_a_err_e = np.zeros(len(fields))
        Q_result_e = np.zeros(len(fields))
        omega_c_e = np.zeros(len(fields))
        omega_c_err_e = np.zeros(len(fields))
        kappa_prod_e = np.zeros(len(fields))
        kappa_prod_err_e = np.zeros(len(fields))
        
        kappa_a2_e = np.zeros(len(fields))
        kappa_a2_err_e = np.zeros(len(fields))
        omega_c2_e = np.zeros(len(fields))
        omega_c2_err_e = np.zeros(len(fields))
        kappa_prod2_e = np.zeros(len(fields))
        kappa_prod2_err_e = np.zeros(len(fields))
        phi21_e = np.zeros(len(fields))
        phi21_err_e = np.zeros(len(fields))
    
        kappa_a3_e = np.zeros(len(fields))
        kappa_a3_err_e = np.zeros(len(fields))
        omega_c3_e = np.zeros(len(fields))
        omega_c3_err_e = np.zeros(len(fields))
        kappa_prod3_e = np.zeros(len(fields))
        kappa_prod3_err_e = np.zeros(len(fields))
        phi31_e = np.zeros(len(fields))
        phi31_err_e = np.zeros(len(fields))

        
for j in field_range:
    
    fig = pl.figure('g%s'%(fields[j]))
    gs = gridspec.GridSpec(1, 2)
    fig.add_subplot(gs[0])
    fig.add_subplot(gs[1])
    fig.axes[1].plot(np.real(data_g[j]),np.imag(data_g[j]), label= 'g field = %sT'%(fields[j]))
    fig.axes[0].plot(freqs,np.abs(data_g[j]), label= 'g field = %sT'%(fields[j]))
#    fig = pl.figure()
#    gs = gridspec.GridSpec(1, 2)
#    fig.add_subplot(gs[0])
#    fig.add_subplot(gs[1])
#    fig.axes[1].plot(np.real(data_e[j]),np.imag(data_e[j]), label= 'e field = %sT'%(fields[j]))
#    fig.axes[0].plot(freqs,np.abs(data_g[j]), label= 'e field = %sT'%(fields[j]))
    if two_modes:    
        params = lmfit.Parameters()
        params.add('kappa_prod1', value=1e8, min = 0)#,vary = False)
        params.add('omega_c', value=10.807e9)#,vary = False)
        params.add('kappa_a1', value=2.2e6, min = 0)#,vary = False)
        if np.max(np.abs(data_g[j])) < limit_for_off:
            params.add('roff',value =(data_g[j][0].real+ data_g[j][-1].real)/2)#,vary = False)
            params.add('ioff',value = (data_g[j][0].imag+ data_g[j][-1].imag)/2)#, vary = False)
        params.add('phi1',value =-1.04, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
            
    
        params.add('kappa_prod2', value= 1e8, min = 0)#,vary = False)
        params.add('omega_c2', value=10.811e9)#,vary = False)
        params.add('kappa_a2', value = 1e6, min = 0)#,vary = False)
        params.add('phi21',value = -1.8, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
        

        result = lmfit.minimize(S21_two_modes_V3, params, args=(freqs,data_g[j]))
        lmfit.report_fit(result.params)
        fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs_model-result.params['omega_c'].value)-(result.params['kappa_a1'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
        if np.max(np.abs(data_g[j])) < limit_for_off:
            fitdata1 = fitdata1 + result.params['roff'].value + 1j*result.params['ioff'].value
        fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs_model-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
        fitdata = fitdata1 + fitdata2
        data_midg[j] = fitdata
        fitdatadB = 20*np.log10(np.abs(fitdata))
        
        fig.axes[0].plot(freqs_model, np.abs(fitdata),'--' )
        fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
#        pl.close()
        xlist[j] = fields[j]
        kappa_a[j] = result.params['kappa_a1'].value
        kappa_a_err[j] = result.params['kappa_a1'].stderr
        Q_result[j] =result.params['omega_c'].value /result.params['kappa_a1'].value
        omega_c[j] = result.params['omega_c'].value
        omega_c_err[j] = result.params['omega_c'].stderr
    
        kappa_prod[j] = result.params['kappa_prod1'].value
        kappa_prod_err[j] = result.params['kappa_prod1'].stderr
        kappa_prod2[j] = result.params['kappa_prod2'].value
        kappa_prod2_err[j] = result.params['kappa_prod2'].stderr
        kappa_a2[j] = result.params['kappa_a2'].value
        kappa_a2_err[j] = result.params['kappa_a2'].stderr
        omega_c2[j] = result.params['omega_c2'].value
        omega_c2_err[j] = result.params['omega_c2'].stderr
        phi21[j] = result.params['phi21'].value
        phi21_err[j] = result.params['phi21'].stderr

    fig = pl.figure('e%s'%(fields[j]))
    gs = gridspec.GridSpec(1, 2)
    fig.add_subplot(gs[0])
    fig.add_subplot(gs[1])
    fig.axes[1].plot(np.real(data_e[j]),np.imag(data_e[j]), label= 'e field = %sT'%(fields[j]))
    fig.axes[0].plot(freqs,np.abs(data_e[j]), label= 'e field = %sT'%(fields[j]))
#    fig = pl.figure()
#    gs = gridspec.GridSpec(1, 2)
#    fig.add_subplot(gs[0])
#    fig.add_subplot(gs[1])
#    fig.axes[1].plot(np.real(data_e[j]),np.imag(data_e[j]), label= 'e field = %sT'%(fields[j]))
#    fig.axes[0].plot(freqs,np.abs(data_g[j]), label= 'e field = %sT'%(fields[j]))
    if two_modes:    
        params = lmfit.Parameters()
        params.add('kappa_prod1', value=1e8, min = 0)#,vary = False)
        params.add('omega_c', value=10.807e9)#,vary = False)
        params.add('kappa_a1', value=2.2e6, min = 0)#,vary = False)
        if np.max(np.abs(data_g[j])) < limit_for_off:
            params.add('roff',value =(data_g[j][0].real+ data_g[j][-1].real)/2)#,vary = False)
            params.add('ioff',value = (data_g[j][0].imag+ data_g[j][-1].imag)/2)#, vary = False)
        params.add('phi1',value =-1.04, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
            
    
        params.add('kappa_prod2', value= 1e8, min = 0)#,vary = False)
        params.add('omega_c2', value=10.811e9)#,vary = False)
        params.add('kappa_a2', value = 1e6, min = 0)#,vary = False)
        params.add('phi21',value = -1.8, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
        

        result = lmfit.minimize(S21_two_modes_V3, params, args=(freqs,data_e[j]))
        lmfit.report_fit(result.params)
        fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs_model-result.params['omega_c'].value)-(result.params['kappa_a1'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
        if np.max(np.abs(data_g[j])) < limit_for_off:
            fitdata1 = fitdata1 + result.params['roff'].value + 1j*result.params['ioff'].value
        fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs_model-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
        fitdata = fitdata1 + fitdata2
        fitdatadB = 20*np.log10(np.abs(fitdata))
        data_mide[j] = fitdata
        
        fig.axes[0].plot(freqs_model, np.abs(fitdata),'--' )
        fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
#        pl.close()
        xlist_e[j] = fields[j]
        kappa_a_e[j] = result.params['kappa_a1'].value
        kappa_a_err_e[j] = result.params['kappa_a1'].stderr
        Q_result_e[j] =result.params['omega_c'].value /result.params['kappa_a1'].value
        omega_c_e[j] = result.params['omega_c'].value
        omega_c_err_e[j] = result.params['omega_c'].stderr
    
        kappa_prod_e[j] = result.params['kappa_prod1'].value
        kappa_prod_err_e[j] = result.params['kappa_prod1'].stderr
        kappa_prod2_e[j] = result.params['kappa_prod2'].value
        kappa_prod2_err_e[j] = result.params['kappa_prod2'].stderr
        kappa_a2_e[j] = result.params['kappa_a2'].value
        kappa_a2_err_e[j] = result.params['kappa_a2'].stderr
        omega_c2_e[j] = result.params['omega_c2'].value
        omega_c2_err_e[j] = result.params['omega_c2'].stderr
        phi21_e[j] = result.params['phi21'].value
        phi21_err_e[j] = result.params['phi21'].stderr
#    if three_modes:
#        change_variables = True
#        params = lmfit.Parameters()
#        params.add('kappa_prod1', value=8.5793e11, min = 0,vary = change_variables)
#        params.add('omega_c', value=10.824e9,vary = change_variables)
#        params.add('kappa_a1', value=3.5e7, min = 0,vary = change_variables)
#        if np.max(np.abs(data_g[j])) < limit_for_off:
##                params.add('roff',value =-0.00197706,vary = change_variables)
##                params.add('ioff',value = 0.00067385, vary = change_variables)
#            params.add('roff',value =(datas[itime][0].real+ datas[itime][-1].real)/2,vary = change_variables)
#            params.add('ioff',value = (datas[itime][0].imag+ datas[itime][-1].imag)/2, vary = change_variables)
#        params.add('phi1',value = -2.6, max = 1.5*np.pi, min = -1.5*np.pi,vary = change_variables)
#            
#    
#        params.add('kappa_prod2', value= 1.9e12, min = 0,vary = change_variables)
#        params.add('omega_c2', value=10.777e9,vary = change_variables)
#        params.add('kappa_a2', value = 9.6e7, min = 0,vary = change_variables)
#        params.add('phi21',value =3.9, max = 1.5*np.pi, min = -1.5*np.pi,vary = change_variables)
#    
#        params.add('kappa_prod3', value= 6e9, min = 0,vary = change_variables)
#        params.add('omega_c3', value=10.807e9,vary = change_variables)
#        params.add('kappa_a3', value = 1.4e6, min = 0,vary = change_variables)
#        params.add('phi31',value =-2, max = 1.5*np.pi, min = -1.5*np.pi,vary = change_variables)
#    #    if itime == 0:
#    #        params = lmfit.Parameters()
#    #        params.add('kappa_prod1', value= 1e9, min = 0)#,vary = False)
#    #        params.add('omega_c', value=10.711e9)#,vary = False)
#    #        params.add('kappa_a', value=2e6, min = 0)#,vary = False)
#    #        if np.max(np.abs(datas)) < limit_for_off:
#    #            params.add('roff',value =(datas[itime][0].real+ datas[itime][-1].real)/2,vary = False)
#    #            params.add('ioff',value = (datas[itime][0].imag+ datas[itime][-1].imag)/2, vary = False)
#    #        params.add('phi1',value = -3, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
#    #                
#    #    
#    #        params.add('kappa_prod2', value= 3e9, min = 0)#,vary = False)
#    #        params.add('omega_c2', value=10.711e9)#,vary = False)
#    #        params.add('kappa_a2', value=1.5e6, min = 0)#,vary = False)
#    #        params.add('phi21',value = 4.2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
#        result = lmfit.minimize(S21_three_modes, params, args=(freqs, datas[itime]))
#        lmfit.report_fit(result.params)
#        fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a1'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
#        if np.max(np.abs(datas[itime])) < limit_for_off:
#            fitdata1 = fitdata1 + result.params['roff'].value + 1j*result.params['ioff'].value
#        fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
#        fitdata3 = np.sqrt(result.params['kappa_prod3'].value)/(-1j*(freqs-result.params['omega_c3'].value)-(result.params['kappa_a3'].value)/2.0 )* np.exp(1j*(result.params['phi31'].value + result.params['phi1'].value))
#        fitdata = fitdata1 + fitdata2 + fitdata3
#        fitdatadB = 20*np.log10(np.abs(fitdata))
#        
#        fig.axes[0].plot(freqs/float(1e9), np.abs(fitdata),'--' )
#        fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
#        xlist[itime] = fields[itime]
#        kappa_a[itime] = result.params['kappa_a1'].value
#        kappa_a_err[itime] = result.params['kappa_a1'].stderr
#        Q_result[itime] =result.params['omega_c'].value /result.params['kappa_a1'].value
#        omega_c[itime] = result.params['omega_c'].value
#        omega_c_err[itime] = result.params['omega_c'].stderr
#        kappa_prod[itime] = result.params['kappa_prod1'].value
#        kappa_prod_err[itime] = result.params['kappa_prod1'].stderr
#
#        kappa_prod2[itime] = result.params['kappa_prod2'].value
#        kappa_prod2_err[itime] = result.params['kappa_prod2'].stderr
#        kappa_a2[itime] = result.params['kappa_a2'].value
#        kappa_a2_err[itime] = result.params['kappa_a2'].stderr
#        omega_c2[itime] = result.params['omega_c2'].value
#        omega_c2_err[itime] = result.params['omega_c2'].stderr
#
#        kappa_prod3[itime] = result.params['kappa_prod3'].value
#        kappa_prod3_err[itime] = result.params['kappa_prod3'].stderr
#        kappa_a3[itime] = result.params['kappa_a3'].value
#        kappa_a3_err[itime] = result.params['kappa_a3'].stderr
#        omega_c3[itime] = result.params['omega_c3'].value
#        omega_c3_err[itime] = result.params['omega_c3'].stderr
#
#        phi21[itime] = result.params['phi21'].value
#        phi21_err[itime] = result.params['phi21'].stderr
#        phi31[itime] = result.params['phi31'].value
#        phi31_err[itime] = result.params['phi31'].stderr




#for i in range(len(fields)):
#    fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a1'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
#    if np.max(np.abs(data_g[j])) < limit_for_off:
#        fitdata1 = fitdata1 + result.params['roff'].value + 1j*result.params['ioff'].value
#    fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
#    fitdata = fitdata1 + fitdata2
    

def int_model(data_mide,data_midg):
#    data_g = np.concatenate((data_lowg,data_midg,data_highg))
#    data_e = np.concatenate((data_lowe,data_mide,data_highe))
    freq_tot = freqs_model/1e9 
    data_g = data_midg
    data_e = data_mide * 2 - data_midg
    I_r = np.zeros((len(freq_tot)))
    I_i = np.zeros((len(freq_tot)))
    for i in range(len(freq_tot)):
        c_in_wg = (1 - np.exp(1j * (freq_tot - 10.811)*12))/((freq_tot - 10.811000000000001))
        c_in_we = (1 - np.exp(-1j * (freq_tot[i] - 10.811)*12))/((freq_tot[i] - 10.811000000000001))
        #c_in_w1 * c_in_w2 *
        integrand =  c_in_wg * c_in_we * data_e[i]*data_g*(np.exp(-1j*(freq_tot[i]-freq_tot)*tf)-1)/((freq_tot[i]-freq_tot+.000000000000001))
#        if i == 0:
#            plt.figure()
#            plt.plot(freq_tot,integrand)
        I_r[i] = np.trapz(np.real(integrand),freq_tot)
        I_i[i] = np.trapz(np.imag(integrand),freq_tot)
#    pl.figure()
#    pl.plot(freq_tot,I_r, label = 'real')
#    pl.plot(freq_tot,I_i, label = 'imag')
#    pl.legend()
#    pl.figure()
#    pl.plot(I_r,I_i)
    final_r = np.trapz(I_r,freq_tot)
    final_i = np.trapz(I_i, freq_tot)
    return [final_r,final_i]
    

deph = np.zeros(len(fields))
stark = np.zeros(len(fields))

for i in range(len(fields)):
    result = int_model(data_mide[i],data_midg[i])
    deph[i] = result[0]
    stark[i] = result[1]

plt.figure()
plt.title('dephasing over field')
plt.xlabel('Field (T)')
plt.ylabel('dephasing at 140 ns')
plt.scatter(fields,deph*1e9, label = 'dephasing')
plt.legend()


plt.figure()
plt.title('stark shift over field')
plt.xlabel('Field (T)')
plt.ylabel('stark shift at 140 ns')
plt.scatter(fields,stark*1e9, label = 'stark shift')
plt.legend()

plt.figure()
plt.scatter(fields, np.abs(deph +1j*stark))

#fields = np.asarray([0,-.005,-.01,-.015,-.02,-.03,-.04,-.05,0,.005,.01,.02,.03,.04,.05])
#
#data_midg_color = np.asarray(list(data_midg)[7:0:-1]+list(data_midg)[8:])
##freq_color = np.asarray(list(freq_mid)[7:0:-1]+list(freq_mid)[8:])
#field_color = np.asarray(list(fields)[7:0:-1]+list(fields)[8:])
#
#
#plt.figure()
#field_color, freq_color = np.meshgrid(field_color, freq_mid)
#plt.pcolormesh(field_color,freq_color,np.transpose(10*np.log10(abs(data_midg_color))))
#plt.colorbar()
#plt.show()






















































