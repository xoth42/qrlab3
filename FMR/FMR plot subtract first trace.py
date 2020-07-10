# -*- coding: utf-8 -*-
"""
Created on Fri Sep 06 15:17:25 2019

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
filepath = r'C:\Users\WangLab\Documents\yingying\0612cooldown\\9mK_18_59_3'

timelist = np.loadtxt(filepath)

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '0827cooldown_circualtor_VNA - Copy.hdf5'
#hdf5_name = '0808cooldown_FMR - Copy (4).hdf5'
date = '20190909'
linewidth = []
fig = pl.figure()
gs = gridspec.GridSpec(1, 2)
fig.add_subplot(gs[0])
fig.add_subplot(gs[1])
#for time in ['135518','144555','153200','162022','165755','173609','181741','185126']:
#for time in ['122746','125127','131643','133959','140913','143530','150150']:
for time in ['102416']:
#for time in timelist[:]:
    time = str(int(time)).zfill(6)
#    experiment = 'Power_Sweep_VNA'
    experiment = 'Magnet_Sweep_VNA'
    fit_S12 = False
    fit_S11 = False
    
    subtract = True
    average = 1
    
    if subtract:
    #    hdf5_name_s = '0531cooldown_FMR.hdf5'
        hdf5_name_s = hdf5_name
        date_s = '20190909'
        time_s = '102416'
        experiment_s = 'Magnet_Sweep_VNA'
    
    def S21(params, x, y):
        est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
        est = est * np.exp(1j*params['phi'])
        if np.max(np.abs(y)) < limit_for_off:
            est = est + params['roff'] + 1j*params['ioff']

        
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
#    exp_ = f['/' + date + '/' + '123511' + '_' + experiment]
    #y_keys.remove(x_key)
    #y_keys.remove(x2_key)
    freq = exp['freqs'].value
#    powers = exp['currents'].value
#    powers = exp['powers'].value
    powers = exp['fields'].value
    real = exp['realS21'].value
    imag = exp['imaginaryS21'].value
#    powers = np.concatenate((exp['fields'].value[::-1], exp_['fields'].value),axis = 0)
#    real = np.concatenate((exp['realS21'].value[::-1], exp_['realS21'].value),axis = 0)
#    imag = np.concatenate((exp['imaginaryS21'].value[::-1], exp_['imaginaryS21'].value),axis = 0)
    f.close()
    if subtract:
        f_s = h5.File(filepath + hdf5_name_s, 'r')
        exp_s = f_s['/' + date_s + '/' + time_s + '_' + experiment_s]
        y_keys_s = exp_s.keys()
        #print(y_keys)
        
        #y_keys.remove(x_key)
        #y_keys.remove(x2_key)
        freq_s = exp_s['freqs'].value
    
        real_s = exp_s['realS21'].value[-1]
        imag_s = exp_s['imaginaryS21'].value[-1]
        f_s.close()
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
    pl.figure()
    figname = ''
    powerplot = np.concatenate((powers, np.zeros(1) + powers[1]-powers[0] + powers[-1]))
    mag = np.sqrt(real**2 + imag**2)
    Z = np.transpose(mag)
    #X,Y = np.meshgrid(field, freq)
    X,Y = np.meshgrid(powerplot, freq)
#    pl.xlim(X.min(), X.max())
    pl.pcolormesh(X,Y/1e9,Z)
    pl.colorbar()
#    
#    pl.title('S33 Stark Drive on Port 3 at 11.2 GHz',fontsize = 14)
    pl.xlabel('Magnetic Field(T)',fontsize = 12)
    pl.ylabel('Frequency(GHz)',fontsize = 12)
    pl.show()
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
    
    for i in range(len(real)/average):
        
        freqs = freq
        datas = np.zeros(len(real[i]),dtype = complex)
        for j in np.linspace(i*average, (i+1) * average , average):
            datas = datas + real[i] + 1j*imag[i]
        datas = datas/average
#        fig = pl.figure()
#        gs = gridspec.GridSpec(1, 2)
#        fig.add_subplot(gs[0])
#        fig.add_subplot(gs[1])
        fig.axes[1].plot(datas.real,datas.imag)#, label= 'power = %sdB'%(powers[i]))
        fig.axes[0].plot(freq/1e9,20*np.log10(np.abs(datas)))#, label= 'power = %sdB'%(powers[i]))
    
    
    
    
    
        
    
        if fit_S12:
            params = lmfit.Parameters()
            params.add('kappa_prod', value=(np.max(np.abs(datas))*5e6)**2.001, min = 0)#, vary = False)
            params.add('omega_c', value=freqs[np.argmax(np.abs(datas))]*1.0002,min = freqs[np.argmax(np.abs(datas))]*0.9995, max = freqs[np.argmax(np.abs(datas))] * 1.0005)#,vary = False)
            params.add('kappa_a', value=10e6, min = 0)#, max = 4e6)#,vary = False)
            if np.max(np.abs(datas)) < limit_for_off:
                params.add('roff',value = 0.5*(np.real(datas[0]+ datas[-1])))#,vary = False)
                params.add('ioff',value = 0.5*(np.imag(datas[0]+ datas[-1])))#, vary = False)
            params.add('phi',value = 2, max = np.pi*1.5, min = -np.pi*1.5)#,vary = False)
                    
        #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
            result = lmfit.minimize(S21, params, args=(freqs, datas))
            lmfit.report_fit(result.params)
    #        print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
            print ('kappa tot: ',result.params['kappa_a'].value/1e6, 'MHz')
            fitdata = np.sqrt(result.params['kappa_prod'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )
            fitdata = fitdata * np.exp(1j*result.params['phi'].value)
            if np.max(np.abs(datas)) < limit_for_off:
                fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
            
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
    #        lmfit.report_fit(result.params)
            print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
            print ('coupling Q: ',result.params['omega_c'].value/result.params['kappa_1'].value)
            fitdata = (-1 - result.params['kappa_1'].value / (-1j*(freqs-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value
            fitdatadB = 20*np.log10(np.abs(fitdata))
    
    
        #    fig.axes[0].set_title(figname)
    #    pl.suptitle(figname)
        if fit_S12 or fit_S11:
            fig.axes[0].plot(freqs/float(1e9), fitdatadB,'--' )
            fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
            xlist[i] = powers[i]
            kappa_a[i] = result.params['kappa_a'].value
            kappa_a_err[i] = result.params['kappa_a'].stderr
            Q_result[i] =result.params['omega_c'].value /result.params['kappa_a'].value
            omega_c[i] = result.params['omega_c'].value
            omega_c_err[i] = result.params['omega_c'].stderr
            if fit_S12:   
                kappa_prod[i] = result.params['kappa_prod'].value
                kappa_prod_err[i] = result.params['kappa_prod'].stderr
    #    pl.xlabel('freq(GHz)')
    
#    fig.axes[1].set_aspect('equal', 'box')
        
#    pl.legend()
#    pl.figure()
    pl.errorbar(xlist, kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa_tot{}'.format(time))

    #pl.xlabel('drive power (dbm)')
#    pl.ylabel('linewidth(MHz)')
#    pl.legend(loc='upper right')
#    pl.show()
pl.show()
    #pl.savefig(save_filepath + 'kappas.png')
    #pl.figure()
    #pl.errorbar(xlist, kappa_prod, yerr = kappa_prod_err, fmt ='o', label='kappa_prod')
    ##pl.xlabel('drive power (dBm)')
    #pl.legend(loc='upper right')
    #pl.figure()
    #pl.scatter(xlist, Q_result, label='total Q')
    ##    pl.xlabel('field(T)')
    ##    pl.xlabel('different measurement')
    ##pl.xlabel('drive power (dBm)')
    #pl.ylabel('Q')
    #pl.legend(loc='upper right')
    ##pl.savefig(save_filepath + 'Qs.png')
#    pl.figure()
#    pl.errorbar(xlist, omega_c/1000000000, yerr = omega_c_err/1000000000, fmt ='o', label='omega_c')
#    #pl.xlabel('drive power (dbm)')
#    pl.ylabel('grequency(GHz)')
#    pl.legend(loc='upper right')
    
    #lin_power = xlist
    ##lin_power = np.power(10,xlist/10)
    ##lin_power[0] = 0
    #pl.figure()
    #pl.scatter(lin_power, omega_c/1e9, label='frequency')
    ##    pl.xlabel('field(T)')
    ##    pl.xlabel('different measurement')
    ##n=19
    ##m,b = np.polyfit(lin_power[0:n],omega_c[0:n]/1e9,1)
    ##print 'frequencu(GHz) = %s * power(mW) + %s'%(m,b)
    ##print 'slope for frequency:', m
    ##pl.plot(lin_power, lin_power*m + b,label = 'frequencu(GHz) = %s * power(mW) + %s'%(m,b))
    ##pl.xlabel('drive power(mW)')
    #pl.ylabel('frequency(GHz)')
    #pl.legend(loc='upper right')
    #
    #pl.figure()
    #pl.scatter(lin_power, Q_result, label='total Q')
    ##    pl.xlabel('field(T)')
    ##    pl.xlabel('different measurement')
    ##pl.xlabel('drive power (mW)')
    #pl.ylabel('Q')
    #pl.legend(loc='upper right')
    #
    #
    #pl.figure()
    #pl.errorbar(lin_power, kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa_tot')
    ##n=6
    ##m,b = np.polyfit(lin_power[0:n],kappa_a[0:n]/1e6,1)
    ##pl.plot(lin_power, lin_power*m + b)
    ##print 'slope for kappa:', m
    ##pl.xlabel('drive power (mW)')
    #pl.ylabel('linewidth(MHz)')
    #pl.legend(loc='upper right')
    #
    #
    #pl.figure()
    #pl.errorbar(lin_power, kappa_prod, yerr = kappa_prod_err, fmt ='o', label='kappa_prod')
    ##pl.xlabel('drive power (mW)')
    #pl.legend(loc='upper right')
    
    
#    linewidth.append(np.average(kappa_a[10:15]))

