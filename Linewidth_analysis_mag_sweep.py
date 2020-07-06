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
from scipy.signal import argrelmax
filepath = r'C:\Users\WangLab\Documents\yingying\0612cooldown\\10mK_19_0_39'

timelist = np.loadtxt(filepath)

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '0808cooldown_FMR - Copy (3).hdf5'
#hdf5_name = '0730cooldown_FMR - Copy.hdf5'
date = '20190812'
time = '193650'
experiment = 'Power_Sweep_Varies_freq_VNA'
linewidth = []
f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
freq_i = exp['freqs'].value

powers_i = exp['powers'].value

real_i = exp['realS21'].value
imag_i = exp['imaginaryS21'].value
mag_i = (real_i**2 + imag_i**2)**.5
#cutoff stuff disregard if min and max are clear
initial_field = .30
initial_freq = 8.472e9
final_field = .30384
final_freq = 8.572e9
def cutoff_line(field):
    y = (field-initial_field)*(final_freq-initial_freq)/(final_field-initial_field) + initial_freq
    return y
freq_n = []
real_n = []
imag_n = []
mag_n = []
limit_for_off = 1
def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
    est = est * np.exp(1j*params['phi'])
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']

    
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    
    
def S11(params, x, y):

    est = (-1 - params['kappa_1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2))*params['A']
    return y - abs(est)
linewidths = []
linewidths_errors = []
#for j in range(len(freq)):
#    pl.figure()
#    pl.plot(freq[j],mag[j])
if 0: # for altering dat by using a cutoff line and/or narrowing down the points
    for i in range(len(freq_i)):
        if cutoff_line(powers_i[i]) < freq_i[i][-1]:
            cutoff_index = np.argmin(abs(freq_i[i]-cutoff_line(powers_i[i])))
            freq_n.append(freq_i[i][0:cutoff_index])
            real_n.append(real_i[i][0:cutoff_index])
            imag_n.append(imag_i[i][0:cutoff_index])
            mag_n.append(mag_i[i][0:cutoff_index])
        else:
            freq_n.append(freq_i[i])
            real_n.append(real_i[i])
            imag_n.append(imag_i[i])
            mag_n.append(mag_i[i])
        max_index = np.argmax(mag_n[i]) #finding minimum point of data, this should be where the qubit is
        if (max_index-200) < 0:
            low_bound = 0
        else:
            low_bound = max_index - 200
        if (max_index + 200) > len(mag_n[i]):
            up_bound_t = len(mag_n[i])-1
        else:
            up_bound_t = max_index + 200
        up_bound = np.argmin(mag_n[i][max_index:up_bound_t]) + max_index
        freq_n[i] = np.array(freq_n[i][low_bound:up_bound-3])
        mag_n[i] = np.array(mag_n[i][low_bound:up_bound-3])
        real_n[i] = np.array(real_n[i][low_bound:up_bound-3])
        imag_n[i] = np.array(imag_n[i][low_bound:up_bound-3])
    #    datas = real_n[i] + 1j*imag_n[i]
        params = lmfit.Parameters()
        params.add('kappa_prod', value=(np.max(mag_n[i])*0.5e6)**2.001, min = 0)#, vary = False)
        params.add('omega_c', value=freq_n[i][np.argmax(mag_n[i])]*1.0002,min = freq_n[i][np.argmax(mag_n[i])]*0.9995, max = freq_n[i][np.argmax(mag_n[i])] * 1.0005)#,vary = False)
        params.add('kappa_a', value=1e6, min = 0)#, max = 4e6)#,vary = False)
        if np.max(mag_n[i]) < limit_for_off:
            params.add('roff',value = 0.5*(real_n[i][0]+ real_n[i][-1]))#,vary = False)
            params.add('ioff',value = 0.5*(imag_n[i][0]+ imag_n[i][-1]))#, vary = False)
        params.add('phi',value = 2, max = np.pi*1.5, min = -np.pi*1.5)#,vary = False)  
        result = lmfit.minimize(S21, params, args=(freq_n[i], (real_n[i]+imag_n[i])))
        lmfit.report_fit(result.params)
        linewidths.append(result.params['kappa_a'])
        linewidths_errors.append(result.params['kappa_a'].stderr)
    pl.figure()
    pl.title('Linewidth variation of yig coupled to cavity through magnet sweep')
    pl.errorbar(powers_i, linewidths,
                yerr=linewidths_errors,
                fmt='o')
    pl.xlabel('Magnetic Field (T)')
    pl.ylabel('Linewidth (10^7 Hz)')
##for time in ['193650']:
###for time in timelist[:]:
##time = str(int(time)).zfill(6)
##experiment = 'Power_Sweep_VNA'
##experiment = 'Magnet_Sweep_VNA'
#fit_S12 = True
#fit_S11 = False
#
#subtract = False
#average = 1
#
#if subtract:
##    hdf5_name_s = '0531cooldown_FMR.hdf5'
#    hdf5_name_s = hdf5_name
#    date_s = '20190617'
#    time_s = '195946'
#    experiment_s = 'SingleTrace'
#
#def S21(params, x, y):
#    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
#    est = est * np.exp(1j*params['phi'])
#    if np.max(np.abs(y)) < limit_for_off:
#        est = est + params['roff'] + 1j*params['ioff']
#
#    
#    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
#    
#    
#def S11(params, x, y):
#
#    est = (-1 - params['kappa_1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2))*params['A']
#    return y - abs(est)
#
#
#limit_for_off = 1
#
#''' Primary x axis and secondary if 2d'''
##x_key = 'freqs'
##x2_key = 'powers'
#
##f = h5.File(filepath + hdf5_name, 'r')
##exp = f['/' + date + '/' + time + '_' + experiment]
##y_keys = exp.keys()
##print(y_keys)
#
##y_keys.remove(x_key)
##y_keys.remove(x2_key)
#freq = freq_n
##    powers = exp['currents'].value
#powers = powers_i
##powers = exp['fields'].value
#real = real_n
#imag = imag_n
#
#if subtract:
#    f_s = h5.File(filepath + hdf5_name_s, 'r')
#    exp_s = f_s['/' + date_s + '/' + time_s + '_' + experiment_s]
#    y_keys_s = exp_s.keys()
#    #print(y_keys)
#    
#    #y_keys.remove(x_key)
#    #y_keys.remove(x2_key)
#    freq_s = exp_s['freqs'].value
#
#    real_s = exp_s['real'].value
#    imag_s = exp_s['imaginary'].value
#
#'''Conversion factor from Yoko current in mA to actual magnetic field in mT'''
##if current.any() < 0.5:
##    field = current*529.37 + 0.49
##else:
##    field = -268.93 * (current)**2 + 839.69*current - 88.67
#
#'''Plot'''
#
#
#if subtract:
#    for i in range(len(real)):
#        real[i] = real[i] - real_s
#        imag[i] = imag[i] - imag_s
#pl.figure()
#figname = ''
#powerplot = np.concatenate((powers, np.zeros(1) + powers[1]-powers[0] + powers[-1]))
#mag = 10*np.log10(real**2 + imag**2)
#Z = np.transpose(mag)
##X,Y = np.meshgrid(field, freq)
#X,Y = np.meshgrid(powerplot, freq)
#pl.xlim(X.min(), X.max())
#pl.pcolormesh(X,Y,Z)
#pl.colorbar()
#
##pl.title('YIG FMR Spectrum, S11 Measurement')
##pl.xlabel('Magnetic Field(mT)')
#pl.ylabel('Frequency(GHz)')
#
#fig = pl.figure()
#gs = gridspec.GridSpec(1, 2)
#fig.add_subplot(gs[0])
#fig.add_subplot(gs[1])
#if fit_S12 or fit_S11:
#    xlist = np.zeros(len(real))
#    kappa_a = np.zeros(len(real))
#    kappa_a_err = np.zeros(len(real))
#    Q_result = np.zeros(len(real))
#    omega_c = np.zeros(len(real))
#    omega_c_err = np.zeros(len(real))
#    kappa_prod = np.zeros(len(real))
#    kappa_prod_err = np.zeros(len(real))
#
#for i in range(len(real)/average):
#    
#    freqs = freq
#    datas = np.zeros(len(real[i]),dtype = complex)
#    for j in np.linspace(i*average, (i+1) * average , average):
#        datas = datas + real[i] + 1j*imag[i]
#    datas = datas/average
#    fig = pl.figure()
#    gs = gridspec.GridSpec(1, 2)
#    fig.add_subplot(gs[0])
#    fig.add_subplot(gs[1])
#    fig.axes[1].plot(datas.real,datas.imag)#, label= 'power = %sdB'%(powers[i]))
#    fig.axes[0].plot(freq/1e9,20*np.log10(np.abs(datas)))#, label= 'power = %sdB'%(powers[i]))
#
#
#
#
#
#    
#
#    if fit_S12:
#        params = lmfit.Parameters()
#        params.add('kappa_prod', value=(np.max(np.abs(datas))*0.5e6)**2.001, min = 0)#, vary = False)
#        params.add('omega_c', value=freqs[np.argmax(np.abs(datas))]*1.0002,min = freqs[np.argmax(np.abs(datas))]*0.9995, max = freqs[np.argmax(np.abs(datas))] * 1.0005)#,vary = False)
#        params.add('kappa_a', value=1e6, min = 0)#, max = 4e6)#,vary = False)
#        if np.max(np.abs(datas)) < limit_for_off:
#            params.add('roff',value = 0.5*(np.real(datas[0]+ datas[-1])))#,vary = False)
#            params.add('ioff',value = 0.5*(np.imag(datas[0]+ datas[-1])))#, vary = False)
#        params.add('phi',value = 2, max = np.pi*1.5, min = -np.pi*1.5)#,vary = False)
#                
#    #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
#        result = lmfit.minimize(S21, params, args=(freqs, datas))
#        lmfit.report_fit(result.params)
##        print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
#        print ('kappa tot: ',result.params['kappa_a'].value/1e6, 'MHz')
#        fitdata = np.sqrt(result.params['kappa_prod'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )
#        fitdata = fitdata * np.exp(1j*result.params['phi'].value)
#        if np.max(np.abs(datas)) < limit_for_off:
#            fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
#        
#        fitdatadB = 20*np.log10(np.abs(fitdata))
#    #    ampdata = 20*np.log10(np.sqrt(realdata[0,:]**2 + imagdata[0,:]**2))
#    if fit_S11:
#        params = lmfit.Parameters()
#        params.add('kappa_1', value=2.1305e+05)
#        params.add('omega_c', value=freqs[np.argmin(np.abs(datas))]*1.0001)
#        params.add('kappa_a', value=3.0022e+06)
#        params.add('A', value=1)
#                
#    #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
#        result = lmfit.minimize(S11, params, args=(freqs, abs(datas)))
##        lmfit.report_fit(result.params)
#        print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
#        print ('coupling Q: ',result.params['omega_c'].value/result.params['kappa_1'].value)
#        fitdata = (-1 - result.params['kappa_1'].value / (-1j*(freqs-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value
#        fitdatadB = 20*np.log10(np.abs(fitdata))
#
#
#    #    fig.axes[0].set_title(figname)
##    pl.suptitle(figname)
#    if fit_S12 or fit_S11:
#        fig.axes[0].plot(freqs/float(1e9), fitdatadB,'--' )
#        fig.axes[1].plot(fitdata.real,fitdata.imag, '--')
#        xlist[i] = powers[i]
#        kappa_a[i] = result.params['kappa_a'].value
#        kappa_a_err[i] = result.params['kappa_a'].stderr
#        Q_result[i] =result.params['omega_c'].value /result.params['kappa_a'].value
#        omega_c[i] = result.params['omega_c'].value
#        omega_c_err[i] = result.params['omega_c'].stderr
#        if fit_S12:   
#            kappa_prod[i] = result.params['kappa_prod'].value
#            kappa_prod_err[i] = result.params['kappa_prod'].stderr
##    pl.xlabel('freq(GHz)')
#
##    fig.axes[1].set_aspect('equal', 'box')
#    
#pl.legend()
#pl.figure()
#pl.errorbar(xlist, kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa_tot')
##pl.xlabel('drive power (dbm)')
#pl.ylabel('linewidth(MHz)')
#pl.legend(loc='upper right')
#pl.show()
##pl.savefig(save_filepath + 'kappas.png')
##pl.figure()
##pl.errorbar(xlist, kappa_prod, yerr = kappa_prod_err, fmt ='o', label='kappa_prod')
###pl.xlabel('drive power (dBm)')
##pl.legend(loc='upper right')
##pl.figure()
##pl.scatter(xlist, Q_result, label='total Q')
###    pl.xlabel('field(T)')
###    pl.xlabel('different measurement')
###pl.xlabel('drive power (dBm)')
##pl.ylabel('Q')
##pl.legend(loc='upper right')
###pl.savefig(save_filepath + 'Qs.png')
#pl.figure()
#pl.errorbar(xlist, omega_c/1000000000, yerr = omega_c_err/1000000000, fmt ='o', label='omega_c')
##pl.xlabel('drive power (dbm)')
#pl.ylabel('grequency(GHz)')
#pl.legend(loc='upper right')
#
##lin_power = xlist
###lin_power = np.power(10,xlist/10)
###lin_power[0] = 0
##pl.figure()
##pl.scatter(lin_power, omega_c/1e9, label='frequency')
###    pl.xlabel('field(T)')
###    pl.xlabel('different measurement')
###n=19
###m,b = np.polyfit(lin_power[0:n],omega_c[0:n]/1e9,1)
###print 'frequencu(GHz) = %s * power(mW) + %s'%(m,b)
###print 'slope for frequency:', m
###pl.plot(lin_power, lin_power*m + b,label = 'frequencu(GHz) = %s * power(mW) + %s'%(m,b))
###pl.xlabel('drive power(mW)')
##pl.ylabel('frequency(GHz)')
##pl.legend(loc='upper right')
##
##pl.figure()
##pl.scatter(lin_power, Q_result, label='total Q')
###    pl.xlabel('field(T)')
###    pl.xlabel('different measurement')
###pl.xlabel('drive power (mW)')
##pl.ylabel('Q')
##pl.legend(loc='upper right')
##
##
##pl.figure()
##pl.errorbar(lin_power, kappa_a/1000000, yerr = kappa_a_err/1000000, fmt ='o', label='kappa_tot')
###n=6
###m,b = np.polyfit(lin_power[0:n],kappa_a[0:n]/1e6,1)
###pl.plot(lin_power, lin_power*m + b)
###print 'slope for kappa:', m
###pl.xlabel('drive power (mW)')
##pl.ylabel('linewidth(MHz)')
##pl.legend(loc='upper right')
##
##
##pl.figure()
##pl.errorbar(lin_power, kappa_prod, yerr = kappa_prod_err, fmt ='o', label='kappa_prod')
###pl.xlabel('drive power (mW)')
##pl.legend(loc='upper right')
#
#
#linewidth.append(np.average(kappa_a[10:15]))
#f.close()
#
#    