# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 22:38:49 2020

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


''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '0626cooldown_circualtor_VNA - Copy.hdf5'

date = '20200702'
#time = '233434'
experiment = 'Power_Sweep_VNA'

fields = np.linspace(0, -0.05,26)
#fields = np.linspace(0.05, 0.002,13)

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'

two_modes = True
three_modes = False

j = 0

final_plot = True

itime = 0

if itime == 0:
    datas = np.zeros([len(fields),1601],dtype = complex)
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
f = h5.File(filepath + hdf5_name, 'r')

#


#freq1 = np.zeros([nrows,len(fields)])
#freq2 = np.zeros([nrows,len(fields)])
#freq1_err = np.zeros([nrows,len(fields)])
#freq2_err = np.zeros([nrows,len(fields)])  

for i, title in enumerate(f[date].keys()):
#    print int(title[0:6])
#    print int(title[0:6]) <= 020617
    if int(title[0:6]) <= int('122000') and int(title[0:6]) > int('043000') and title[7:12] =='Power':
        print title



        x_key = 'freqs'
        #x2_key = 'powers'
        exp = f[date][title]
#    exp = f['/' + date1 + '/' + time + '_' + experiment]
        y_keys = exp.keys()
        #print(y_keys)
        
        #y_keys.remove(x_key)
        #y_keys.remove(x2_key)
        freq = exp['freqs'].value
        #current = exp['currents'].value
#        powers = exp['powers'].value
        real = exp['realS21'].value
        imag = exp['imaginaryS21'].value
        
        datas[itime] = real[j] + 1j * imag[j]
        
        '''Conversion factor from Yoko current in mA to actual magnetic field in mT'''
        #if current.any() < 0.5:
        #    field = current*529.37 + 0.49
        #else:
        #    field = -268.93 * (current)**2 + 839.69*current - 88.67
        
        '''Plot'''
        freqs = freq
        fig = pl.figure()
        gs = gridspec.GridSpec(1, 2)
        fig.add_subplot(gs[0])
        fig.add_subplot(gs[1])
        fig.axes[1].plot(real[j],imag[j], label= 'field = %sT'%(fields[itime]))
        fig.axes[0].plot(freq/1e9,np.abs(datas[itime]), label= 'field = %sT'%(fields[itime]))
        if two_modes:    
            params = lmfit.Parameters()
            params.add('kappa_prod1', value=1e7, min = 0)#,vary = False)
            params.add('omega_c', value=10.808e9)#,vary = False)
            params.add('kappa_a1', value=1e7, min = 0)#,vary = False)
            if np.max(np.abs(datas)) < limit_for_off:
                params.add('roff',value =(datas[itime][0].real+ datas[itime][-1].real)/2)#,vary = False)
                params.add('ioff',value = (datas[itime][0].imag+ datas[itime][-1].imag)/2)#, vary = False)
            params.add('phi1',value =2, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
                
        
            params.add('kappa_prod2', value= 1e5, min = 0)#,vary = False)
            params.add('omega_c2', value=10.825e9)#,vary = False)
            params.add('kappa_a2', value = 2.4221e6, min = 0)#,vary = False)
            params.add('phi21',value =3.154, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
            
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
            result = lmfit.minimize(S21_two_modes_V3, params, args=(freqs, datas[itime]))
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
            params.add('kappa_prod1', value=1.86e11, min = 0,vary = change_variables)
            params.add('omega_c', value=10.807e9,vary = change_variables)
            params.add('kappa_a1', value=3e6, min = 0,vary = change_variables)
            if np.max(np.abs(datas[itime])) < limit_for_off:
#                params.add('roff',value =-0.00197706,vary = change_variables)
#                params.add('ioff',value = 0.00067385, vary = change_variables)
                params.add('roff',value =(datas[itime][0].real+ datas[itime][-1].real)/2,vary = change_variables)
                params.add('ioff',value = (datas[itime][0].imag+ datas[itime][-1].imag)/2, vary = change_variables)
            params.add('phi1',value = 4.71, max = 1.5*np.pi, min = -1.5*np.pi,vary = change_variables)
                
        
            params.add('kappa_prod2', value= 1.75e11, min = 0,vary = change_variables)
            params.add('omega_c2', value=10.807e9,vary = change_variables)
            params.add('kappa_a2', value = 2.8902e6, min = 0,vary = change_variables)
            params.add('phi21',value =-3.2, max = 1.5*np.pi, min = -1.5*np.pi,vary = change_variables)
        
            params.add('kappa_prod3', value= 7.68e8, min = 0,vary = change_variables)
            params.add('omega_c3', value=10.808e9,vary = change_variables)
            params.add('kappa_a3', value = 2.1133e6, min = 0,vary = change_variables)
            params.add('phi31',value =4.711, max = 1.5*np.pi, min = -1.5*np.pi,vary = change_variables)
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
    figname = ''
    fieldplot = np.concatenate((fields, np.zeros(1) + fields[1]-fields[0] + fields[-1]))
    mag = 20*np.log10(np.abs(datas))
    Z = np.transpose(mag)
    #X,Y = np.meshgrid(field, freq)
    X,Y = np.meshgrid(fieldplot, freq)
    pl.xlim(X.min(), X.max())
    pl.pcolormesh(X,Y,Z,vmax = -30, vmin = -80)
    pl.colorbar()
    #pl.title('YIG FMR Spectrum, S11 Measurement')
    #pl.xlabel('Magnetic Field(mT)')
    pl.ylabel('Frequency(GHz)')
    #pl.close()
    f.close()
        
        
    lin_power = xlist
    #lin_power = np.power(10,xlist/10)
    #lin_power[0] = 0
    if two_modes:
        pl.figure()
        pl.errorbar(lin_power, omega_c/1e9, yerr =omega_c_err/1e9, fmt ='o', label='frequency')
        pl.errorbar(lin_power, omega_c2/1e9, yerr =omega_c2_err/1e9, fmt ='o', label='frequency')
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
