# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 13:05:45 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:41:20 2019

@author: Wang_Lab
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as pl
#from t1t2_plotting import smart_T1_delays
import os
import time
import math
import lmfit
import time
import datetime
Magnet = mclient.instruments['Magnet']
#f= open("C:\Users\Wang_Lab\Documents\yingying\%s.txt"%(time.strftime('%Y%m%d_%H%M%S', time.localtime())),"w+")
#fields = [-0.035,0.035,-0.04,0.04,-0.045,0.045,-0.05,0.05]
fields=[0]
#powers_list = [[-23,0],[-25,0],[-18,10]]
powers_list = [[0, 0]]
#freqs = np.linspace(10.65e9,10.9e9,51)
#freqs = np.linspace(10.60e9,10.84e9,25)
#fields = np.linspace(-0.06,-0.03,16)
#powers = [-25]

#freqs_list = [np.linspace(10.6e9,10.604e9,5), np.linspace(10.65e9,10.654e9,5),np.linspace(10.75e9,10.754e9,5),np.linspace(10.8e9,10.804e9,5)]
freqs_list = [np.linspace(10.711e9,10.711e9,150)] #, np.linspace(10.708e9,10.716e9,17), np.linspace(10.708e9,10.716e9,17), np.linspace(10.708e9,10.716e9,17) ]
#freqs = np.linspace(10.8e9,10.804e9,5)
SSdrive = mclient.instruments['SS_drive']
freq_range = np.linspace(-30e6, 3e6, 81)
freq_range2 = np.linspace(-15e6, 1e6, 81)

do_cav_spec = True

readout_info = mclient.get_readout_info('readout')
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit2_info = mclient.get_qubit_info('qubit2ge')
readout = mclient.instruments['readout']


for ifield, field in enumerate(fields):
    if float(Magnet.do_get_PSwitch())==1:
#        Magnet.do_set_field(0)
#        time.sleep(600)
        
        Magnet.do_set_field(field)
        print('set Magnet field to %s'%(field))
        time.sleep(900)
        Magnet.do_set_PSwitch(0)
        print('set PSwitch heater off')
        
        time.sleep(400)


#        amp = np.zeros((len(freqs),51))
        
    if do_cav_spec:
        from single_cavity import rocavspectroscopy_keysight
        rofreq = 10.715e9
        freq_r = 10e6
        ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-3, 10, 1),
                                             np.linspace(rofreq-freq_r, rofreq+freq_r, 101),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
        ro.measure()
        max_freq = 10.7174e9
#        max_freq = ro.freqs[np.argmax(ro.ampdata[0])]
        print max_freq
        readout_info.rfsource1.set_frequency(max_freq)
        readout_info.rfsource2.set_frequency(max_freq+50e6)

    for ilist,freqs in enumerate(freqs_list):
        powers = powers_list[ilist]
        fit_freq = np.zeros((len(fields),len(freqs)))

        fit_freq_err = np.zeros((len(fields),len(freqs)))

        fit_freq2 = np.zeros((len(fields),len(freqs)))

        fit_freq2_err = np.zeros((len(fields),len(freqs)))
        
        amp1 = np.zeros((len(fields),len(freqs)))

        amp2 = np.zeros((len(fields),len(freqs)))
                
        amp1_err = np.zeros((len(fields),len(freqs)))

        amp2_err = np.zeros((len(fields),len(freqs)))
    
        phase = np.zeros((len(freqs),len(freq_range)))

        phase2 = np.zeros((len(freqs),len(freq_range)))


            
            
        for ifreq, freq in enumerate(freqs[0:len(freqs)]):


            
        
    
    
    
    #            from single_qubit import efrabi
    #
    #            dig.set_naverages(5000)
    #            efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.6, 0.6, 101), first_pi=True,second_pi=True, seq=None, generate=True, update=True,
    #                                    proj_func='phase')
    #            efr.measure_keysight()
    #            period = efr.fit_params['period'].value
    #            amp = efr.fit_params['amp'].value
    #            dig.set_naverages(10000)
    #            efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.6, 0.6, 101), first_pi=False, second_pi=True, selective=False, seq=None, generate=True,
    #                                    force_period = period, proj_func='phase')
    #            efr.measure_keysight()
    #            ampe = efr.fit_params['amp'].value
    #            print('power = %s dB     %s / %s = %s'%(power, ampe, amp, ampe/amp))
    #            pl.title('power = %s dB     %s / %s = %s'%(power, ampe, amp, ampe/amp))
    #            dig.set_naverages(5000)
    #        if abs(field) <= 0.01:
    #            ro_freq = 10.936e9
    #            ro_freq2 = 10.934e9
    #        elif abs(field <= 0.025):
    #            ro_freq = 10.935e9
    #            ro_freq2 = 10.932e9
    #        else:
    #            ro_freq = 10.934e9
    #            ro_freq2 = 10.932e9            
    #                
    #        readout_info.rfsource1.set_frequency(ro_freq)
    #        readout_info.rfsource2.set_frequency(ro_freq+50e6)
    #        time.sleep(0.1)
            
    
            
    

    
            dig.set_naverages(40000)    
                
            from single_qubit import ssbspec_gaussianfit
    
            seq = sequencer.Trigger(600)
            
            spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, freq_range, seq=seq, plot_seqs=False, proj_func='amplitude')
            spec.measure_keysight()
            for j in range(len(freq_range)):
                 phase[ifreq][j] = spec.pp_data[j] 
                 
            
            if np.max(phase[ifreq]) - np.min(phase[ifreq])>300:
                for iphase in range(len(phase[ifreq])):
                    if phase[ifreq][iphase] > 0:
                        phase[ifreq][iphase] = phase[ifreq][iphase] -360
                        
            
#            phase[ifreq] = phase[ifreq] - np.average(phase[ifreq])            
                
                 
            fit_freq[ifield][ifreq] = spec.fit_params['freq'].value
            fit_freq_err[ifield][ifreq] = spec.fit_params['freq'].stderr
            amp1[ifield][ifreq] = spec.fit_params['off'].value
            amp1_err[ifield][ifreq] = spec.fit_params['off'].stderr
            pl.close()
            
            
            
           
    

            dig.set_naverages(20000)
    
    
            from single_qubit import ssbspec_gaussianfit
    
            seq = sequencer.Trigger(600)
            
            spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, freq_range2, seq=seq, plot_seqs=False, proj_func='amplitude')
            spec.measure_keysight()
    
            for j in range(len(freq_range2)):
                 phase2[ifreq][j] = spec.pp_data[j] 
                 
            
            if np.max(phase[ifreq]) - np.min(phase[ifreq])>300:
                for iphase in range(len(phase[ifreq])):
                    if phase2[ifreq][iphase] > 0:
                        phase2[ifreq][iphase] = phase2[ifreq][iphase] -360
                        
            
#            phase2[ifreq] = phase2[ifreq] - np.average(phase2[ifreq])            
            fit_freq2[ifield][ifreq] = spec.fit_params['freq'].value
            fit_freq2_err[ifield][ifreq] = spec.fit_params['freq'].stderr 
            amp2[ifield][ifreq] = spec.fit_params['off'].value
            amp2_err[ifield][ifreq] = spec.fit_params['off'].stderr
                 
            pl.close()
            
            
            
        
        freqsplot = np.concatenate([freqs, np.asarray([freqs[1] - freqs[0] + freqs[-1]])])
        freqsplot = np.linspace(1,len(freqs),len(freqs))
        X, Y = np.meshgrid(freqsplot, freq_range)
        Zp = np.transpose(phase)
        pl.figure()
        pl.pcolormesh(X,Y,Zp)
        pl.title('phase, power = %s dB field = %s T'%(powers[0],field))
        pl.colorbar()
        fn = os.path.join(r'C:\_Data', 'images/%s_projection.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        pl.savefig(fn, **kwargs) 
        
        X, Y = np.meshgrid(freqsplot, freq_range2)
        Zp = np.transpose(phase2)
        pl.figure()
        pl.pcolormesh(X,Y,Zp)
        pl.title('phase qubit2, power = %s dB field = %s T'%(powers[1],field))
        pl.colorbar()
        fn = os.path.join(r'C:\_Data', 'images/%s_qubit2_projection.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        pl.savefig(fn, **kwargs) 
        Zp0 = np.transpose(phase20)
       
        pl.close()
        pl.close()

        pl.figure()
        pl.errorbar(np.linspace(1,len(freqs),len(freqs)), fit_freq[ifield]/1e6, yerr = fit_freq_err[ifield]/1e6,label = 'qubit 1,SS on, %.03f +/- %.03f MHz  max = %.03f +/- %.03f MHz '%(np.average(fit_freq[ifield]/1e6),np.average(fit_freq_err[ifield]/1e6),fit_freq[ifield][np.argmin(fit_freq[ifield])]/1e6,fit_freq_err[ifield][np.argmin(fit_freq[ifield])]/1e6))
        pl.errorbar(np.linspace(1,len(freqs),len(freqs)), fit_freq2[ifield]/1e6, yerr = fit_freq2_err[ifield]/1e6,label = 'qubit 2,SS on, %.03f +/- %.03f MHz  max = %.03f +/- %.03f MHz'%(np.average(fit_freq2[ifield]/1e6),np.average(fit_freq2_err[ifield]/1e6),fit_freq2[ifield][np.argmin(fit_freq2[ifield])]/1e6,fit_freq2_err[ifield][np.argmin(fit_freq2[ifield])]/1e6))
        pl.title('Stark Shift frequency @ field = %s T, power = %s '%(field,powers))
        pl.legend()
        fn = os.path.join(r'C:\_Data', 'images/%s_fit_freqs.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        pl.savefig(fn, **kwargs)
        
        pl.figure()
        pl.errorbar(np.linspace(1,len(freqs),len(freqs)), amp1[ifield],yerr = amp1_err[ifield],label = 'qubit 1,SS on,amp ')
        pl.errorbar(np.linspace(1,len(freqs),len(freqs)), amp2[ifield],yerr = amp2_err[ifield],label = 'qubit 2,SS on, amp')
        pl.title('amp @ field = %s T, power = %s '%(field,powers))
        pl.legend()
        fn = os.path.join(r'C:\_Data', 'images/%s_amps.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        pl.savefig(fn, **kwargs)
    if do_cav_spec:
        from single_cavity import rocavspectroscopy_keysight
        rofreq = 10.715e9
        freq_r = 10e6
        ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-3, 10, 1),
                                             np.linspace(rofreq-freq_r, rofreq+freq_r, 101),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
        ro.measure()

    if len(fields)>1:
            
        Magnet.do_set_PSwitch(1)
        time.sleep(60)