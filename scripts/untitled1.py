# -*- coding: utf-8 -*-
"""
Created on Tue May  5 00:23:41 2020

@author: Wang_Lab
"""
import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import os
import time
import math
import lmfit
import time
import datetime

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
qubit2_info = mclient.get_qubit_info('qubit2ge')
ef2_info = mclient.get_qubit_info('qubit2ef')
ef2_V2_info = mclient.get_qubit_info('qubit2ef_V2')
#fwm_info = mclient.get_qubit_info('fwm_info1')
#fwm2_info = mclient.get_qubit_info('fwm_info2')
#qubit03_info = mclient.get_qubit_info('qubit1_03')
#qubit14_info = mclient.get_qubit_info('qubit1_14')
readout_info = mclient.get_readout_info('readout')
readout = mclient.instruments['readout']
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')


fields = [-0.025, 0.02,-0.015, 0.01, -0.005, 0.0025, -0.001,0.0005,-0.00025, 0]

fields = - np.asarray(fields)
Magnet.do_set_PSwitch(1)
time.sleep(35)




dig.set_naverages(6000)

for field in fields:
    if abs(field)>0.01:
        Magnet.do_set_field(0)
        time.sleep(600)

    

#            
    Magnet.do_set_field(field)
    time.sleep(600)




fields =np.linspace(-0.024,-0.03, 4)
Magnet.do_set_PSwitch(1)
print('heating PSwitch')
time.sleep(40)
Magnet.do_set_field(fields[0])
print('setting field')
time.sleep(1000)


for field in fields:
    if 1:
        Magnet.do_set_PSwitch(1)
        print('heating PSwitch')
        time.sleep(40)
#        Magnet.do_set_field(0)
#        print('setting field')
#        time.sleep(1800)
        Magnet.do_set_field(field)
        print('setting field')
        time.sleep(100)
        Magnet.do_set_PSwitch(0)
        print('cooling PSwitch')
        time.sleep(350)
#    freqs = np.linspace(10.80e9,10.82e9,21)
    freqs = np.linspace(10.81e9,10.81e9,51)
#    freqs = np.linspace(10.813e9,10.813e9,3)
    freq_range = np.linspace(-4e6, 2e6, 81)
    
    powers = np.zeros(len(freqs))
#    powers= [10,10,10,10,10,9,8,6,4,2,0,1,3,4,4,5,7,10,10,10,10]
#    powers = [4,4,4]
    phase = np.zeros((len(freqs),len(freq_range)))
    phase0 = np.zeros((len(freqs),len(freq_range)))
    fit_freq = np.zeros(len(freqs))
    fit_freq0 = np.zeros(len(freqs))
    fit_freq_err = np.zeros(len(freqs))
    fit_freq0_err = np.zeros(len(freqs))
    SSdrive = mclient.instruments['SS_drive']
    for ifreq, freq in enumerate(freqs):
        SSdrive.set_power(powers[ifreq])
        SSdrive.set_frequency(freq)
        time.sleep(0.1)
        SSdrive.set_rf_on(True)
        time.sleep(0.1)
    
        from single_qubit import ssbspec_gaussianfit_SS
    
        seq = sequencer.Trigger(600)
        spec = ssbspec_gaussianfit_SS.SSBSpec_Gaussianfit_SS(qubit2_info, freq_range, seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
        for j in range(len(freq_range)):
             phase[ifreq][j] = spec.pp_data[j] 
             
        
        if np.max(phase[ifreq]) - np.min(phase[ifreq])>300:
            for iphase in range(len(phase[ifreq])):
                if phase[ifreq][iphase] > 0:
                    phase[ifreq][iphase] = phase[ifreq][iphase] -360
                    
        
        phase[ifreq] = phase[ifreq] - np.average(phase[ifreq])            
            
             
        fit_freq[ifreq] = spec.fit_params['freq'].value
        fit_freq_err[ifreq] = spec.fit_params['freq'].stderr
        plt.close()
        
        
        
        
        SSdrive.set_rf_on(False)
        time.sleep(0.1)
        from single_qubit import ssbspec_gaussianfit
    
        seq = sequencer.Trigger(600)
        
        spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, freq_range, seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
        for j in range(len(freq_range)):
             phase0[ifreq][j] = spec.pp_data[j] 
    
        
        if np.max(phase0[ifreq]) - np.min(phase0[ifreq])>300:
            for iphase in range(len(phase0[ifreq])):
                if phase0[ifreq][iphase] > 0:
                    phase0[ifreq][iphase] = phase0[ifreq][iphase] -360
                    
        
        phase0[ifreq] = phase0[ifreq] - np.average(phase0[ifreq])            
            
             
        fit_freq0[ifreq] = spec.fit_params['freq'].value
        fit_freq0_err[ifreq] = spec.fit_params['freq'].stderr
        plt.close()
        
    if freqs[0] == freqs[1]:
        freqs = np.asarray(range(len(freqs)))
    freqsplot = np.concatenate([freqs, np.asarray([freqs[1] - freqs[0] + freqs[-1]])]) 
    freq_rangeplot = np.concatenate([freq_range, np.asarray([freq_range[1] - freq_range[0] + freq_range[-1]])])      
    X, Y = np.meshgrid(freqsplot, freq_rangeplot)
    Zp = np.transpose(phase)
    plt.figure()
    plt.pcolormesh(X,Y,Zp)
    plt.title('%sT phase, power = %s dB'%(field, powers[0]))
    plt.colorbar()
    fn = os.path.join(r'C:\_Data', 'images/%s_%sT_phase.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()), field))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs) 
    Zp0 = np.transpose(phase0)
    plt.figure()
    plt.pcolormesh(X,Y,Zp0)
    plt.title('%sT, phase SSdrive off, power = %s dB'%(field , powers[0]))
    plt.colorbar()
    fn = os.path.join(r'C:\_Data', 'images/%s_phase0.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)
    
    plt.figure()
    plt.errorbar(freqs/1e6, fit_freq/1e6, yerr = fit_freq_err/1e6,label = 'SS on, %.03f +/- %.03f MHz'%(np.average(fit_freq/1e6),np.average(fit_freq_err/1e6)))
    plt.errorbar(freqs/1e6, fit_freq0/1e6, yerr = fit_freq0_err/1e6,label = 'SS off, %.03f +/- %.03f MHz'%(np.average(fit_freq0/1e6),np.average(fit_freq0_err/1e6)))
    plt.ylabel('MHz')
    plt.legend()
    fn = os.path.join(r'C:\_Data', 'images/%s_%sT_fit_freqs.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()), field))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)
    
    freqs = np.linspace(10.80e9,10.82e9,21)
#    freqs = np.linspace(10.81e9,10.81e9,51)
#    freqs = np.linspace(10.813e9,10.813e9,3)
    freq_range = np.linspace(-14e6, 2e6, 81)
#    powers = np.zeros(len(freqs))
    powers= [10,10,10,10,10,9,8,6,4,2,0,1,3,4,4,5,7,10,10,10,10]
#    powers = [4,4,4]
    phase = np.zeros((len(freqs),len(freq_range)))
    phase0 = np.zeros((len(freqs),len(freq_range)))
    fit_freq = np.zeros(len(freqs))
    fit_freq0 = np.zeros(len(freqs))
    fit_freq_err = np.zeros(len(freqs))
    fit_freq0_err = np.zeros(len(freqs))
    SSdrive = mclient.instruments['SS_drive']
    for ifreq, freq in enumerate(freqs):
        SSdrive.set_power(powers[ifreq])
        SSdrive.set_frequency(freq)
        time.sleep(0.1)
        SSdrive.set_rf_on(True)
        time.sleep(0.1)
    
        from single_qubit import ssbspec_gaussianfit_SS
    
        seq = sequencer.Trigger(600)
        spec = ssbspec_gaussianfit_SS.SSBSpec_Gaussianfit_SS(qubit2_info, freq_range, seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
        for j in range(len(freq_range)):
             phase[ifreq][j] = spec.pp_data[j] 
             
        
        if np.max(phase[ifreq]) - np.min(phase[ifreq])>300:
            for iphase in range(len(phase[ifreq])):
                if phase[ifreq][iphase] > 0:
                    phase[ifreq][iphase] = phase[ifreq][iphase] -360
                    
        
        phase[ifreq] = phase[ifreq] - np.average(phase[ifreq])            
            
             
        fit_freq[ifreq] = spec.fit_params['freq'].value
        fit_freq_err[ifreq] = spec.fit_params['freq'].stderr
        plt.close()
        
        
        
        
        SSdrive.set_rf_on(False)
        time.sleep(0.1)
        from single_qubit import ssbspec_gaussianfit
    
        seq = sequencer.Trigger(600)
        
        spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, freq_range, seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
        for j in range(len(freq_range)):
             phase0[ifreq][j] = spec.pp_data[j] 
    
        
        if np.max(phase0[ifreq]) - np.min(phase0[ifreq])>300:
            for iphase in range(len(phase0[ifreq])):
                if phase0[ifreq][iphase] > 0:
                    phase0[ifreq][iphase] = phase0[ifreq][iphase] -360
                    
        
        phase0[ifreq] = phase0[ifreq] - np.average(phase0[ifreq])            
            
             
        fit_freq0[ifreq] = spec.fit_params['freq'].value
        fit_freq0_err[ifreq] = spec.fit_params['freq'].stderr
        plt.close()
        
    if freqs[0] == freqs[1]:
        freqs = np.asarray(range(len(freqs)))
    freqsplot = np.concatenate([freqs, np.asarray([freqs[1] - freqs[0] + freqs[-1]])]) 
    freq_rangeplot = np.concatenate([freq_range, np.asarray([freq_range[1] - freq_range[0] + freq_range[-1]])])      
    X, Y = np.meshgrid(freqsplot, freq_rangeplot)
    Zp = np.transpose(phase)
    plt.figure()
    plt.pcolormesh(X,Y,Zp)
    plt.title('%sT, phase, power = %s dB'%(field, powers[0]))
    plt.colorbar()
    fn = os.path.join(r'C:\_Data','images/%s_%sT_phase.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()), field))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs) 
    Zp0 = np.transpose(phase0)
    plt.figure()
    plt.pcolormesh(X,Y,Zp0)
    plt.title('%sT, phase SSdrive off, power = %s dB'%(field, powers[0]))
    plt.colorbar()
    fn = os.path.join(r'C:\_Data', 'images/%s_%sT_phase0.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()), field))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)
    
    plt.figure()
    plt.errorbar(freqs/1e6, fit_freq/1e6, yerr = fit_freq_err/1e6,label = 'SS on, %.03f +/- %.03f MHz'%(np.average(fit_freq/1e6),np.average(fit_freq_err/1e6)))
    plt.errorbar(freqs/1e6, fit_freq0/1e6, yerr = fit_freq0_err/1e6,label = 'SS off, %.03f +/- %.03f MHz'%(np.average(fit_freq0/1e6),np.average(fit_freq0_err/1e6)))
    plt.ylabel('MHz')
    plt.legend()
    fn = os.path.join(r'C:\_Data', 'images/%s_%s_fit_freqs.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),field))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    plt.savefig(fn, **kwargs)