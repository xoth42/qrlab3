# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 18:56:30 2021

@author: WangLab
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 22:38:49 2020

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

datas = np.loadtxt(r'C:\Users\WangLab\Documents\circulator results\2021-03-11 16-09-18\\0to0.05colorplot_Z.txt')

datas = datas[:len(datas)/2] + 1j * datas[len(datas)/2:]
datas_p_plot = np.transpose(datas)

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
    
def S21_two_modes_V4(params, x, y):
    
    A = params['kappa_a1']/2 - 1j *(x-params['omega_c1'])
    B = params['kappa_a2']/2 - 1j *(x-params['omega_c2'])
    C = params['kappa_a3']/2 - 1j *(x-params['omega_c3'])
    D =  - 1j *(x-params['omega_c4'])
    est = 1j * np.sqrt(params['kappa_1']*params['kappa_a3'])
#    est = np.sqrt(params['kappa_prod1'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )* np.exp(1j*params['phi1'])
#    if np.max(np.abs(y)) < limit_for_off:
#        est = est + params['roff'] + 1j*params['ioff']
#    est = est + np.sqrt(params['kappa_prod2'])/(-1j*(x-params['omega_c2'])-(params['kappa_a2'])/2.0 ) * np.exp(1j*(params['phi21']+params['phi1']))

    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
limit_for_off = 1



fields = np.linspace(0,-0.05,26)
#fields = np.linspace(0.05, 0.002,13)

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'
all_field = False
new_fig = False
two_modes = True
three_modes = False


final_plot =False

itime = 0 #index of the field being analyzed so you can save your place and work on only fitting a few fields at a time

save_data = False
num_fits = 2
#if itime == 0:
#    datas = np.zeros([len(fields),1601],dtype = complex)
if two_modes:
    if itime == 0:
        
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
if three_modes:
    if itime == 0:
        
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
#timelist = ['182908','185023','191139','193255','195410','201527','203643','205759','211915','214032','220149','222305','224423',
#            '230540','232657','234815','000932','003049','005207','011324','013442','015601','021719','023837','025955','032114']
##timelist = ['190211','193554','200936','204319','211703','215046','222429','225812','233156','000540','003923','011308','014652']
#for itime, time in enumerate(timelist):
#    if int(time) < 120000:
#        date1 = str(int(date) + 1)
#    else:
#        date1 = date
#            
#    f = h5.File(filepath + hdf5_name, 'r')
#f = h5.File(filepath + hdf5_name, 'r')

#

freq = np.linspace(10.78e9,10.85e9,1601)
#freq1 = np.zeros([nrows,len(fields)])
#freq2 = np.zeros([nrows,len(fields)])
#freq1_err = np.zeros([nrows,len(fields)])
#freq2_err = np.zeros([nrows,len(fields)])  

for i in range(num_fits):

        '''Plot'''
        freqs = freq
        fig = pl.figure()
        gs = gridspec.GridSpec(1, 2)
        fig.add_subplot(gs[0])
        fig.add_subplot(gs[1])
        fig.axes[1].plot(np.real(datas[itime]),np.imag(datas[itime]), label= 'field = %sT'%(fields[itime]))
        fig.axes[0].plot(freq/1e9,np.abs(datas[itime]), label= 'field = %sT'%(fields[itime]))
        if two_modes:    
            params = lmfit.Parameters()
            params.add('kappa_prod1', value=2e11, min = 0)#,vary = False)
            params.add('omega_c', value=10.81e9, vary = True)#,vary = False)
            params.add('kappa_a1', value=7e6, min = 0)#,vary = False)
            if np.max(np.abs(datas)) < limit_for_off:
                params.add('roff',value =(datas[itime][0].real+ datas[itime][-1].real)/2)#,vary = False)
                params.add('ioff',value = (datas[itime][0].imag+ datas[itime][-1].imag)/2)#, vary = False)
            params.add('phi1',value =-2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
                
        
            params.add('kappa_prod2', value=1e10, min = 0)#,vary = False)
            params.add('omega_c2', value=10.8045e9)#,vary = False)
            params.add('kappa_a2', value = 5e6, min = 0)#,vary = False)
            params.add('phi21',value = -2.4, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
            
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

            xs = freqs[480:1600]
            ys = datas[itime][480:1600]
            result = lmfit.minimize(S21_two_modes_V3, params, args=(xs,ys))
            lmfit.report_fit(result.params)
            fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a1'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
            if np.max(np.abs(datas)) < limit_for_off:
                fitdata1 = fitdata1 + result.params['roff'].value + 1j*result.params['ioff'].value
            fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
            fitdata = fitdata1 + fitdata2
            fitdatadB = 20*np.log10(np.abs(fitdata))
            
            fig.axes[0].plot(freqs/float(1e9), np.abs(fitdata),'--' )
            fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
    #        pl.close()
            xlist[itime] = fields[itime]
            kappa_a[itime] = result.params['kappa_a1'].value
            kappa_a_err[itime] = result.params['kappa_a1'].stderr
            Q_result[itime] =result.params['omega_c'].value /result.params['kappa_a1'].value
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
        if three_modes:
            change_variables = True
            params = lmfit.Parameters()
            params.add('kappa_prod1', value=2.55e10, min = 0,vary = change_variables)
            params.add('omega_c', value=10.811e9,vary = change_variables)
            params.add('kappa_a1', value=2.2e6, min = 0,vary = change_variables)
            if np.max(np.abs(datas[itime])) < limit_for_off:
#                params.add('roff',value =-0.00197706,vary = change_variables)
#                params.add('ioff',value = 0.00067385, vary = change_variables)
                params.add('roff',value =(datas[itime][0].real+ datas[itime][-1].real)/2,vary = change_variables)
                params.add('ioff',value = (datas[itime][0].imag+ datas[itime][-1].imag)/2, vary = change_variables)
            params.add('phi1',value = 0, max = 1.5*np.pi, min = -1.5*np.pi,vary = change_variables)
                
        
#            params.add('kappa_prod2', value= 7e11, min = 0,vary = change_variables)
#            params.add('omega_c2', value=10.8e9, vary = change_variables)
#            params.add('kappa_a2', value =60e6,vary = change_variables)
#            params.add('phi21',value =-2.5, max = 1.5*np.pi, min = -1.5*np.pi,vary = change_variables)
            params.add('kappa_prod2', value= 0, vary = False)
            params.add('omega_c2', value=10.785e9,vary = False)
            params.add('kappa_a2', value =8e7, min = 0,vary = False)
            params.add('phi21',value =-2.5, max = 1.5*np.pi, min = -1.5*np.pi,vary = False)
        
            params.add('kappa_prod3', value= 1.2e9, min = 0,vary = change_variables)
            params.add('omega_c3', value=10.804e9, vary = change_variables)
            params.add('kappa_a3', value =3e6,vary = change_variables)
            params.add('phi31',value =-1.93, max = 1.5*np.pi, min = -1.5*np.pi,vary = change_variables)
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
            result = lmfit.minimize(S21_three_modes, params, args=(freqs, datas[itime]))
            lmfit.report_fit(result.params)
            fitdata1 = np.sqrt(result.params['kappa_prod1'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a1'].value)/2.0 )* np.exp(1j*result.params['phi1'].value)
            if np.max(np.abs(datas[itime])) < limit_for_off:
                fitdata1 = fitdata1 + result.params['roff'].value + 1j*result.params['ioff'].value
            fitdata2 = np.sqrt(result.params['kappa_prod2'].value)/(-1j*(freqs-result.params['omega_c2'].value)-(result.params['kappa_a2'].value)/2.0 )* np.exp(1j*(result.params['phi21'].value + result.params['phi1'].value))
            fitdata3 = np.sqrt(result.params['kappa_prod3'].value)/(-1j*(freqs-result.params['omega_c3'].value)-(result.params['kappa_a3'].value)/2.0 )* np.exp(1j*(result.params['phi31'].value + result.params['phi1'].value))
            fitdata = fitdata1 + fitdata2 + fitdata3
            fitdatadB = 20*np.log10(np.abs(fitdata))
            
            fig.axes[0].plot(freqs/float(1e9), np.abs(fitdata),'--' )
            fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
            xlist[itime] = fields[itime]
            kappa_a[itime] = result.params['kappa_a1'].value
            kappa_a_err[itime] = result.params['kappa_a1'].stderr
            Q_result[itime] =result.params['omega_c'].value /result.params['kappa_a1'].value
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

            kappa_prod3[itime] = result.params['kappa_prod3'].value
            kappa_prod3_err[itime] = result.params['kappa_prod3'].stderr
            kappa_a3[itime] = result.params['kappa_a3'].value
            kappa_a3_err[itime] = result.params['kappa_a3'].stderr
            omega_c3[itime] = result.params['omega_c3'].value
            omega_c3_err[itime] = result.params['omega_c3'].stderr

            phi21[itime] = result.params['phi21'].value
            phi21_err[itime] = result.params['phi21'].stderr
            phi31[itime] = result.params['phi31'].value
            phi31_err[itime] = result.params['phi31'].stderr
        itime = itime + 1
if final_plot: 

    pl.figure()
    matplotlib.rc('xtick', labelsize=24) 
    matplotlib.rc('ytick', labelsize=24)
    figname = ''
    axis_font = {'fontname':'Arial', 'size':'24'}
    fieldplot = np.concatenate((fields, np.zeros(1) + fields[1]-fields[0] + fields[-1]))
    mag = 20*np.log10(np.abs(datas))
    Z = np.transpose(mag)#-mag2)
    #X,Y = np.meshgrid(field, freq)
    X,Y = np.meshgrid(fieldplot, freq)
    pl.xlim(X.min(), X.max())
#    pl.pcolormesh(X,Y/1e9,Z,vmax = 40, vmin = 0, cmap = 'RdBu')
#    pl.pcolormesh(X,Y/1e9,Z,vmax = -10,vmin = -100)
#    mag2 = 20*np.log10(np.abs(datas2))
#    Z2 = np.transpose(mag2)
#    #X,Y = np.meshgrid(field, freq)
#    X,Y = np.meshgrid(fieldplot, freq)
#    pl.xlim(X.min(), X.max())
    pl.pcolormesh(X,Y/1e9,Z)#,vmax = -30, vmin = -80)
#    cbar = pl.colorbar()
#    cbar.set_label('dB',rotation=0, **axis_font)
    pl.colorbar()
#    pl.title('Color Plot Experiment S31 Spectrum in dB')
    pl.xlabel('Magnetic Field(T)', **axis_font)
    pl.ylabel('Frequency(GHz)', **axis_font)
    #pl.close()

#    f.close()
        
        
    lin_power = fields
    #lin_power = np.power(10,xlist/10)
    #lin_power[0] = 0
    if two_modes:
        pl.figure()
        pl.errorbar(lin_power, omega_c/1e9, yerr =omega_c_err/1e9, fmt ='o', label='frequency')
        pl.errorbar(lin_power, omega_c2/1e9, yerr =omega_c2_err/1e9, fmt ='o', label='frequency')
        print 'omega_c\n', omega_c
        print omega_c
    if three_modes:
        pl.figure()
        pl.errorbar(lin_power, omega_c/1e9, yerr =omega_c_err/1e9, fmt ='o', label='frequency1')
        pl.errorbar(lin_power, omega_c2/1e9, yerr =omega_c2_err/1e9, fmt ='o', label='frequency2')
        pl.errorbar(lin_power, omega_c3/1e9, yerr =omega_c3_err/1e9, fmt ='o', label='frequency3')
    #    pl.xlabel('field(T)')
    #    pl.xlabel('different measurement')
    #n=19
    #m,b = np.polyfit(lin_power[0:n],omega_c[0:n]/1e9,1)
    #print 'frequencu(GHz) = %s * power(mW) + %s'%(m,b)
    #print 'slope for frequency:', m
    #pl.plot(lin_power, lin_power*m + b,label = 'frequencu(GHz) = %s * power(mW) + %s'%(m,b))
    #pl.xlabel('drive power(mW)')
    pl.ylabel('frequency(GHz)')
    pl.legend(loc='upper right')
    
    #pl.figure()
    #pl.scatter(lin_power, Q_result, label='total Q')
    ##    pl.xlabel('field(T)')
    ##    pl.xlabel('different measurement')
    ##pl.xlabel('drive power (mW)')
    #pl.ylabel('Q')
    #pl.legend(loc='upper right')
    
    
    if two_modes:
        pl.figure()
        pl.errorbar(lin_power, kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa_tot')
        pl.errorbar(lin_power, kappa_a2/1000000, yerr = kappa_a2_err/1000000, fmt ='o')
    if three_modes:
        pl.figure()
        pl.errorbar(lin_power, kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa1')
        pl.errorbar(lin_power, kappa_a2/1000000, yerr = kappa_a2_err/1000000, fmt ='o', label='kappa2')
        pl.errorbar(lin_power, kappa_a3/1000000, yerr = kappa_a3_err/1000000, fmt ='o', label='kappa3')
    #n=6
    #m,b = np.polyfit(lin_power[0:n],kappa_a[0:n]/1e6,1)
    #pl.plot(lin_power, lin_power*m + b)
    #print 'slope for kappa:', m
    #pl.xlabel('drive power (mW)')
    pl.ylabel('linewidth(MHz)')
    pl.legend(loc='upper right')
    
    #
    if two_modes:
        pl.figure()
        pl.errorbar(lin_power, kappa_prod, yerr = kappa_prod_err, fmt ='o', label='kappa_prod')
        pl.errorbar(lin_power, kappa_prod2, yerr = kappa_prod2_err, fmt ='o')
    if three_modes:
        pl.figure()
        pl.errorbar(lin_power, kappa_prod, yerr = kappa_prod_err, fmt ='o', label='kappa_prod1')
        pl.errorbar(lin_power, kappa_prod2, yerr = kappa_prod2_err, fmt ='o', label='kappa_prod2')
        pl.errorbar(lin_power, kappa_prod3, yerr = kappa_prod3_err, fmt ='o', label='kappa_prod3')
    #pl.xlabel('drive power (mW)')
    pl.legend(loc='upper right')    
        
    if two_modes:    
        pl.figure()
        pl.errorbar(lin_power,phi21, yerr = phi21_err, fmt ='o', label='phi21')
    if three_modes:
        pl.figure()
        pl.errorbar(lin_power,phi21, yerr = phi21_err, fmt ='o', label='phi21')
        pl.errorbar(lin_power,phi31, yerr = phi31_err, fmt ='o', label='phi31')
    #pl.xlabel('drive power (mW)')
    pl.legend(loc='upper right') 
#    data = np.concatenate([omega_c, omega_c2, kappa_a,kappa_a2])
#    np.savetxt('C:\Users\WangLab\Documents\yingying\\0317cooldown_S21 cavity freqs and kappas.txt', data)
    
    


if save_data: #printing all values
#    print('omega_c',omega_c)
#    print('omega_c_err',omega_c_err)
#    print('omega_c2',omega_c2)
#    print('omega_c2_err',omega_c2_err)
#    print('kappa_a',kappa_a)
#    print('kappa_a_err',kappa_a_err)
#    print('kappa_a2',kappa_a2)
#    print('kappa_a2_err',kappa_a2_err)
#    print('kappa_prod',kappa_prod)
#    print('kappa_prod_err',kappa_prod_err)
#    print('kappa_prod2',kappa_prod2)
#    print('kappa_prod2_err',kappa_prod2_err)
#    print('phi21',phi21)
#    print('ph
    if two_modes:
        '''Save the data for later analysis'''
        end_time = date + '_' + title[0:6]
        main_filepath = 'C:/Users/WangLab/Documents/circulator results/'
        time_stamp = end_time
        save_filepath = main_filepath + ''.join(time_stamp) + '/'
        
        
        if not os.path.exists(save_filepath):
            os.makedirs(save_filepath)
            
        np.savetxt(save_filepath + 'results.txt',
                   np.column_stack((fields,omega_c, omega_c_err, omega_c2, omega_c2_err,kappa_a, kappa_a_err,kappa_a2,kappa_a2_err, kappa_prod, kappa_prod_err, kappa_prod2,
                                    kappa_prod2_err, phi21, phi21_err)),
                   header = 
                   
                   'fields,omega_c, omega_c_err, omega_c2, omega_c2_err,kappa_a, kappa_a_err,kappa_a2,kappa_a2_err, kappa_prod, kappa_prod_err, kappa_prod2, kappa_prod2_err, phi21, phi21_err')
    
    if three_modes:
        '''Save the data for later analysis'''
        end_time = date + '_' + title[0:6]
        main_filepath = 'C:/Users/WangLab/Documents/circulator results/'
        time_stamp = end_time
        save_filepath = main_filepath + ''.join(time_stamp) + '/'
        
        
        if not os.path.exists(save_filepath):
            os.makedirs(save_filepath)
            
        np.savetxt(save_filepath + 'three_mode_results_neg.txt',
                   np.column_stack((fields,omega_c, omega_c_err, omega_c2, omega_c2_err,omega_c3, omega_c3_err, 
                                    kappa_a, kappa_a_err,kappa_a2,kappa_a2_err, kappa_a3, kappa_a3_err,
                                    kappa_prod, kappa_prod_err, kappa_prod2,kappa_prod2_err,kappa_prod3,kappa_prod3_err,
                                     phi21, phi21_err, phi31, phi31_err)),
                   header = 
                   
                   'fields,omega_c, omega_c_err, omega_c2, omega_c2_err,omega_c3, omega_c3_err, kappa_a, kappa_a_err,kappa_a2,kappa_a2_err,kappa_a3,kappa_a3_err, kappa_prod, kappa_prod_err, kappa_prod2, kappa_prod2_err,kappa_prod3, kappa_prod3_err, phi21, phi21_err, phi31,phi31_err')



if all_field:
    fig = pl.figure('all_field')
    if new_fig:
        fig = pl.figure('all_field')
        gs = gridspec.GridSpec(1, 1)

        fig.add_subplot(gs[0])
#        fig.axes[i].set_title('%s%s'%(fig_name,self.Sij[i]))
        fig.axes[0].set_xlim(-0.051, 0.051)
        fig.axes[0].set_ylim(10.78,10.83)

#        fig.axes[i].pcolormesh(x, y, z,vmax=np.max(z))#,vmin = np.max([np.min(z),-200]))

    fieldplot = np.concatenate((fields - 0.5*(fields[1]-fields[0]), np.zeros(1) + fields[1]-fields[0] + fields[-1]))
    mag = 20*np.log10(np.abs(datas))
    Z = np.transpose(mag)#-mag2)
    #X,Y = np.meshgrid(field, freq)
    X,Y = np.meshgrid(fieldplot, freq)
#    pl.xlim(X.min(), X.max())
#    pl.pcolormesh(X,Y/1e9,Z,vmax = 40, vmin = 0, cmap = 'RdBu')
#    pl.pcolormesh(X,Y/1e9,Z,vmax = -10,vmin = -100)
#    mag2 = 20*np.log10(np.abs(datas2))
#    Z2 = np.transpose(mag2)
#    #X,Y = np.meshgrid(field, freq)
#    X,Y = np.meshgrid(fieldplot, freq)
#    pl.xlim(X.min(), X.max())
    pl.pcolormesh(X,Y/1e9,Z, vmax = -10, vmin = -50)#,vmax = -30, vmin = -80)
                       
#    pl.colorbar()                  
    end_time = list(str(datetime.datetime.now())[:19])
    end_time[13] = '-'
    end_time[16] = '-'
    main_filepath = 'C:/Users/WangLab/Documents/circulator results/'
    time_stamp = end_time
    save_filepath = main_filepath + ''.join(time_stamp) + '/'
    
    
    if not os.path.exists(save_filepath):
        os.makedirs(save_filepath)
        
    np.savetxt(save_filepath + '0to0.05colorplot_Z.txt',
               np.concatenate([datas.real,datas.imag]))























