# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 00:50:07 2020

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
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import os
import time
import math
import lmfit
import time
import datetime
readout_info = mclient.get_readout_info('readout')
ro_freq = 10.710e9
power = 10
readout_info.rfsource1.set_frequency(ro_freq)
readout_info.rfsource1.set_power(power)
readout_info.rfsource2.set_frequency(ro_freq+50e6)

#time.sleep(1800)

Magnet = mclient.instruments['Magnet']
#fields = [0.03,-0.025, 0.02,-0.015, 0.01, -0.005, 0.0025, -0.001,0.0005,-0.00025, 0]
#fields = - np.asarray(fields)

#dig.set_naverages(6000)
#for field in fields:
#    if abs(field)>0.01:
#        Magnet.do_set_field(0)
#        print('set Magnet field to 0'%(field))
#        time.sleep(600)
#
#    
#
##            
#    Magnet.do_set_field(field)
#    print('set Magnet field to %s'%(field))
#    time.sleep(600)
#f= open("C:\Users\Wang_Lab\Documents\yingying\%s.txt"%(time.strftime('%Y%m%d_%H%M%S', time.localtime())),"w+")
#fields = [-0.035,0.035,-0.04,0.04,-0.045,0.045,-0.05,0.05]
fields=[-0.03]
#fields = np.concatenate((np.linspace(0.02,0.05,16),np.linspace(0.05,0.02,16)))
#powers_list = [[-23,0],[-25,0],[-18,10]]
#powers_list = [[-25, -25]]
#freqs = np.linspace(10.65e9,10.9e9,51)
#freqs = np.linspace(10.60e9,10.84e9,25)
#fields = np.linspace(-0.06,-0.03,16)
power = -6

#freqs_list = [np.linspace(10.6e9,10.604e9,5), np.linspace(10.65e9,10.654e9,5),np.linspace(10.75e9,10.754e9,5),np.linspace(10.8e9,10.804e9,5)]
#freqs_list = [np.linspace(10.708e9,10.716e9,17)] #, np.linspace(10.708e9,10.716e9,17), np.linspace(10.708e9,10.716e9,17), np.linspace(10.708e9,10.716e9,17) ]
#powers = [6,3,1,-1,-3,  -8,-10,-10,-10,-9,  -7,-4,-2,0,3,   6,8   ]
#powers = np.asarray(powers) + 2
#freqs_list = [np.linspace(10.71e9,10.712e9,5)] #, np.linspace(10.708e9,10.716e9,17), np.linspace(10.708e9,10.716e9,17), np.linspace(10.708e9,10.716e9,17) ]
#powers = [1.2,  -3.3,-6,-5.5,-5   ]
freqs = np.concatenate((np.linspace(10.71e9,10.71e9,101),np.linspace(10.7105e9,10.7105e9,101),np.linspace(10.711e9,10.711e9,101),np.linspace(10.7115e9,10.7115e9,101),np.linspace(10.712e9,10.712e9,101)))
powers = np.concatenate((np.zeros(101)+1.2,np.zeros(101)-3.3,np.zeros(101)-6,np.zeros(101)-5.5,np.zeros(101)-5))
#freqs_list = [np.linspace(10.712e9,10.712e9,101)] #, np.linspace(10.708e9,10.716e9,17), np.linspace(10.708e9,10.716e9,17), np.linspace(10.708e9,10.716e9,17) ]
#powers = np.zeros(101) -5
#powers = [-5,-5,-5,-5,-5]
powers = np.asarray(powers) + 2
#freqs = np.linspace(10.8e9,10.804e9,5)
#freqs = freqs_list[0]
SSdrive = mclient.instruments['SS_drive']
freq_range = np.linspace(-30e6, 3e6, 81)
freq_range2 = np.linspace(-15e6, 2e6, 81)
do_cav_spec = False
readout_info = mclient.get_readout_info('readout')
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit2_info = mclient.get_qubit_info('qubit2ge')
readout = mclient.instruments['readout']

fit_freq2 = np.zeros((len(fields),len(freqs)))
fit_freq20 = np.zeros((len(fields),len(freqs)))
fit_freq2_err = np.zeros((len(fields),len(freqs)))
fit_freq20_err = np.zeros((len(fields),len(freqs)))

SSdrive.set_power(power)
SSdrive.set_rf_on(False)
for ifield, field in enumerate(fields):
    if float(Magnet.do_get_PSwitch())==1:
#        Magnet.do_set_field(0)
#        time.sleep(600)
        
        Magnet.do_set_field(field)
        print('set Magnet field to %s'%(field))
        time.sleep(30)
        Magnet.do_set_PSwitch(0)
        print('set PSwitch heater off')
        
        time.sleep(400)


#        amp = np.zeros((len(freqs),51))
        
    if do_cav_spec:
        from single_cavity import rocavspectroscopy_keysight
        rofreq = 10.933e9
        freq_r = 5e6
        ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(10, 10, 1),
                                             np.linspace(rofreq-freq_r, rofreq+freq_r, 101),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
        ro.measure()
#        max_freq = ro.fit_params[2]
        max_freq = ro.freqs[np.argmax(ro.ampdata[0])]
        print max_freq
        readout_info.rfsource1.set_frequency(max_freq)
        readout_info.rfsource2.set_frequency(max_freq+50e6)
    from single_qubit import rabi
#    dig.set_naverages(20000) 
#    #    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
#    tr = rabi.Rabi(qubit_info, 
#    #                               np.linspace(-0.3, 0.3, 81), selective=False,
#                               np.linspace(-0.5, 0.5, 81), selective=False,
#    #                               np.linspace(-0.03, 0.03, 81), selective=True,
#    #                               np.linspace(-0.006, 0.006, 81), selective=True,
#        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
#                               plot_seqs=False, generate=True, repeat_pulse=1,# seq=seq,postseq = postseq,
#                               update=False, #extra_info=[qubit2_info, ef2_info],
#                               proj_func='projection')
#    tr.measure_keysight()
#    pl.close()
#    if np.abs(tr.avg_data[np.argmax(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]) < np.abs(tr.avg_data[np.argmin(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]):
#        qubit1_g = tr.avg_data[np.argmax(abs(tr.avg_data))]
#        qubit1_e = tr.avg_data[np.argmin(abs(tr.avg_data))]
#        
#    else:
#        qubit1_g = tr.avg_data[np.argmin(abs(tr.avg_data))]
#        qubit1_e = tr.avg_data[np.argmax(abs(tr.avg_data))]
#
#    print abs(tr.avg_data[np.argmax(abs(tr.avg_data))]- tr.avg_data[np.argmin(abs(tr.avg_data))])
    dig.set_naverages(10000)     
    tr = rabi.Rabi(qubit2_info, 
    #                               np.linspace(-0.3, 0.3, 81), selective=False,
                               np.linspace(-0.8, 0.8, 81), selective=False,
    #                               np.linspace(-0.03, 0.03, 81), selective=True,
    #                               np.linspace(-0.006, 0.006, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1,# seq=seq,postseq = postseq,
                               update=False, #extra_info=[qubit2_info, ef2_info],
                               proj_func='amplitude')
    tr.measure_keysight()
    pl.close()

    if np.abs(tr.avg_data[np.argmax(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]) < np.abs(tr.avg_data[np.argmin(abs(tr.avg_data))] - tr.avg_data[len(tr.amps)/2]):
        qubit2_g = tr.avg_data[np.argmax(abs(tr.avg_data))]
        qubit2_e = tr.avg_data[np.argmin(abs(tr.avg_data))]
        
    else:
        qubit2_g = tr.avg_data[np.argmin(abs(tr.avg_data))]
        qubit2_e = tr.avg_data[np.argmax(abs(tr.avg_data))]

    print abs(tr.avg_data[np.argmax(abs(tr.avg_data))]- tr.avg_data[np.argmin(abs(tr.avg_data))])





    phase2 = np.zeros((len(freqs),len(freq_range)))
    phase20 = np.zeros((len(freqs),len(freq_range)))   
        
    for ifreq, freq in enumerate(freqs[0:len(freqs)]):
        
        SSdrive.set_frequency(freq)
        time.sleep(0.1)
        SSdrive.set_power(powers[ifreq])
        SSdrive.set_rf_on(True)
        time.sleep(0.1)
        
    




        
        
        

        


        

        readout.set_IQg(qubit2_g)
        readout.set_IQe(qubit2_e)
#        dig.set_naverages(6000)


        from single_qubit import ssbspec_gaussianfit_SS

        seq = sequencer.Trigger(600)
        
        spec = ssbspec_gaussianfit_SS.SSBSpec_Gaussianfit_SS(qubit2_info, freq_range2, seq=seq, plot_seqs=False, proj_func='projection')
        spec.measure_keysight()

        for j in range(len(freq_range2)):
             phase2[ifreq][j] = spec.pp_data[j] 
             
        

                    
        
#        phase2[ifreq] = phase2[ifreq] - np.average(phase2[ifreq])            
        fit_freq2[ifield][ifreq] = spec.fit_params['freq'].value
        fit_freq2_err[ifield][ifreq] = spec.fit_params['freq'].stderr            
             
        pl.close()
        
        
        
        
        SSdrive.set_rf_on(False)
        time.sleep(0.1)
        from single_qubit import ssbspec_gaussianfit

        seq = sequencer.Trigger(600)
        
        spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, freq_range2, seq=seq, plot_seqs=False, proj_func='amplitude')
        spec.measure_keysight()

        for j in range(len(freq_range2)):
             phase20[ifreq][j] = spec.pp_data[j] 

        

                    
        
#        phase20[ifreq] = phase20[ifreq] - np.average(phase20[ifreq])            
            
             
        fit_freq20[ifield][ifreq] = spec.fit_params['freq'].value
        fit_freq20_err[ifield][ifreq] = spec.fit_params['freq'].stderr    
        pl.close()
        
    freqsplot = np.concatenate([freqs, np.asarray([freqs[1] - freqs[0] + freqs[-1]])])
    freqsplot = np.linspace(1,len(freqs),len(freqs))

    X, Y = np.meshgrid(freqsplot, freq_range2)
    Zp = np.transpose(phase2)
    pl.figure()
    pl.pcolormesh(X,Y,Zp)
    pl.title('phase qubit2, power = %s dB field = %s T'%(power,field))
    pl.colorbar()
    fn = os.path.join(r'C:\_Data', 'images/%s_qubit2_projection.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    pl.savefig(fn, **kwargs) 
    Zp0 = np.transpose(phase20)
    pl.figure()
    pl.pcolormesh(X,Y,Zp0)
    pl.title('phase qubit2 SSdrive off, power = %s dB field = %s T'%(power,field))
    pl.colorbar()
    fn = os.path.join(r'C:\_Data', 'images/%s_qubit2_projection0.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    pl.savefig(fn, **kwargs)
    pl.close()
    pl.close()

#    pl.figure()
#    pl.errorbar(freqs/1e6, fit_freq2[ifield]/1e6, yerr = fit_freq2_err[ifield]/1e6,label = 'qubit 2,SS on, %.03f +/- %.03f MHz  max = %.03f +/- %.03f MHz'%(np.average(fit_freq2[ifield]/1e6),np.average(fit_freq2_err[ifield]/1e6),fit_freq2[ifield][np.argmin(fit_freq2[ifield])]/1e6,fit_freq2_err[ifield][np.argmin(fit_freq2[ifield])]/1e6))
#    pl.errorbar(freqs/1e6, fit_freq20[ifield]/1e6, yerr = fit_freq20_err[ifield]/1e6,label = 'qubit 2, SS off, %.03f +/- %.03f MHz'%(np.average(fit_freq20[ifield]/1e6),np.average(fit_freq20_err[ifield]/1e6)))
#    pl.title('Stark Shift frequency @ field = %s T, power = %s '%(field,power))
#    pl.legend()
#    fn = os.path.join(r'C:\_Data', 'images/%s_fit_freqs.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    pl.savefig(fn, **kwargs)
    pl.figure()
    pl.errorbar(np.linspace(1,len(freqs),len(freqs)), fit_freq2[ifield]/1e6, yerr = fit_freq2_err[ifield]/1e6,label = 'qubit 2,SS on, %.03f +/- %.03f MHz  max = %.03f +/- %.03f MHz'%(np.average(fit_freq2[ifield]/1e6),np.average(fit_freq2_err[ifield]/1e6),fit_freq2[ifield][np.argmin(fit_freq2[ifield])]/1e6,fit_freq2_err[ifield][np.argmin(fit_freq2[ifield])]/1e6))
    pl.errorbar(np.linspace(1,len(freqs),len(freqs)), fit_freq20[ifield]/1e6, yerr = fit_freq20_err[ifield]/1e6,label = 'qubit 2, SS off, %.03f +/- %.03f MHz'%(np.average(fit_freq20[ifield]/1e6),np.average(fit_freq20_err[ifield]/1e6)))
    pl.title('Stark Shift frequency @ field = %s T, power = %s '%(field,power))
    pl.legend()
    fn = os.path.join(r'C:\_Data', 'images/%s_fit_freqs.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    pl.savefig(fn, **kwargs)
    
    if len(fields)>1:
        
        Magnet.do_set_PSwitch(1)
        time.sleep(60)
        
        
#qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
#qubit2_info = mclient.get_qubit_info('qubit2ge')
#ef2_info = mclient.get_qubit_info('qubit2ef')
#ef2_V2_info = mclient.get_qubit_info('qubit2ef_V2')
#
##fwm_info = mclient.get_qubit_info('fwm_info1')
##fwm2_info = mclient.get_qubit_info('fwm_info2')
##qubit03_info = mclient.get_qubit_info('qubit1_03')
##qubit14_info = mclient.get_qubit_info('qubit1_14')
#readout_info = mclient.get_readout_info('readout')
##cavity_infoA = mclient.get_qubit_info('cavityAlice')
##RO_info = mclient.get_qubit_info('RO')
##qubit2_info = mclient.get_qubit_info('cavityAlice')
#os.chdir(r'C:/qrlab/scripts')
#
#fields = [0.04,-0.03, 0.02,-0.015, 0.01, -0.005, 0.0025, -0.001,0.0005,-0.00025, 0]
##fields = - np.asarray(fields)
##Magnet.do_set_PSwitch(1)
##time.sleep(35)
##fields = np.linspace(0,0.06,61)
#
##Magnet.do_set_PSwitch(1)
##time.sleep(35)
#
#
#
#dig.set_naverages(6000)
#for field in fields:
#    if abs(field)>0.01:
#        Magnet.do_set_field(0)
#        time.sleep(600)
#
#    
#
##            
#    Magnet.do_set_field(field)
#    time.sleep(600)
#
#
#
#    from single_cavity import rocavspectroscopy_keysight
##    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
##    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
##    Yoko.do_set_current(-0.00175)
#    rofreq = 10.715e9
#    freq_range = 10e6
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(10, 10, 1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 201),
#                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#    
##by Yingying
#    plt.close()
#    plt.close()
#    plt.figure('amp  %sT'%(field))
#    label = ' qubit in g state, field = %sT'%(field)
#    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
#    plt.legend()
#    plt.figure('phase  %sT'%(field))
#    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
#    plt.legend()
##    ga = ro.ampdata[0]
##    gp = ro.phasedata[0]
##    g = ga * np.exp(1j*(gp/180 * np.pi))
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(10, 10, 1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 201),
#                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#    plt.close()
#    plt.close()
#    plt.figure('amp  %sT'%(field))
#    label = ' qubit1 in e state'
#    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
#    plt.legend()
#    plt.figure('phase  %sT'%(field))
#    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
#    plt.legend()
#    
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10, 10, 1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 201),
#                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
#    ro.measure()
#    plt.close()
#    plt.close()
#    plt.figure('amp  %sT'%(field))
#    label = ' qubit2 in e state'
#    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
#    plt.legend()
#    plt.figure('phase  %sT'%(field))
#    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
#    plt.legend()
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit2_info, np.linspace(10,10,1),
#                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
#                                             qubit_pulse=False, seq=seq ,extra_info=[ef2_info])
#    ro.measure()
#    plt.close()
#    plt.close()
#    plt.figure('amp  %sT'%(field))
#    label = ' qubit2 in f state'
#    plt.plot(ro.freqs, ro.ampdata[0],label = label) 
#    plt.legend()
#    fn = os.path.join(r'C:\_Data', 'images/%s_amp%sT.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),field))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    plt.savefig(fn, **kwargs)
#    
#    plt.figure('phase  %sT'%(field))
#    plt.plot(ro.freqs, ro.phasedata[0],label = label)   
#    plt.legend()
#    fn = os.path.join(r'C:\_Data', 'images/%s_phase%sT.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime()),field))
#    fdir = os.path.split(fn)[0]
#    if not os.path.isdir(fdir):
#        os.makedirs(fdir)
#    kwargs = dict()
#    plt.savefig(fn, **kwargs)
