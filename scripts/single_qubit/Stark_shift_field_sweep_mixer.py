# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 17:19:02 2020

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
mixer_info1 = mclient.get_qubit_info('mixer_info1')
mixer_info2 = mclient.get_qubit_info('mixer_info2')
mixer_info1_set = mclient.instruments['mixer_info1']
mixer_info2_set = mclient.instruments['mixer_info2']
SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
SS_mixer_info1_set = mclient.instruments['SS_mixer_info1']
#ef2_V2_info = mclient.get_qubit_info('qubit2ef_V2')

#fwm_info = mclient.get_qubit_info('fwm_info1')
#fwm2_info = mclient.get_qubit_info('fwm_info2')
#qubit03_info = mclient.get_qubit_info('qubit1_03')
#qubit14_info = mclient.get_qubit_info('qubit1_14')
readout_info = mclient.get_readout_info('readout')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')

#fields = [-0.05,0.04,-0.035,0.03,-0.025,0.02,-0.015,0.01,-0.005, 0.0025, -0.001,0.0005,-0.00025, 0]
#fields = - np.asarray(fields)
#Magnet.do_set_PSwitch(1)
#time.sleep(1000)
mixer1_amp = 0.7
mixer_info1_set.set_pi_amp(mixer1_amp)
    
base_ = []
shift_ = []
errors = []
dig.set_naverages(40000)
dig.do_set_trigger_period(100)
fields = np.linspace(-.05,-.05,1)
#RO_freqs = [10.805e9,10.805e9,10.804e9,10.806e9,10.807e9,10.808e9]
RO_freqs = [10.805e9]
stark_drive_deltaf = [-94e6,-94e6,-93e6,-95.5e6,-98.5e6,-98e6]

for i,field in enumerate(fields):
#    if abs(field)>0.01:
#        Magnet.do_set_field(0)
#        time.sleep(600)

    
#    Magnet.do_set_PSwitch(1)
#    print('heating PSwitch')
#    time.sleep(35)
#            
#    Magnet.do_set_field(field)
#    print('setting field')
#    time.sleep(60)
#    Magnet.do_set_PSwitch(0)
#    print('cooling PSwitch')
#    time.sleep(350)
    
    ro_freq = RO_freqs[-i]
#    power = 10
    readout_info.rfsource1.set_frequency(ro_freq - mixer_info1.deltaf)
#    readout_info.rfsource1.set_power(power)
#    readout_info.rfsource1.set_rf_on(True)
#    readout_info.rfsource2.set_power(10)
#    readout_info.rfsource2.set_rf_on(True)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    
    SS_mixer_info1_set.set_deltaf(stark_drive_deltaf[-i])
    SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')

    from single_qubit import stark_shift_with_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    for i in range(1):        
#        RObrick.do_set_power(i)
        seq = sequencer.Trigger(600)
#        seq = Join([seq, qubit2_info.rotate(np.pi/2, X_AXIS)])
        spec = stark_shift_with_mixer.Stark_shift_with_mixer(qubit2_info, mixer_info1, mixer_info2 ,SS_mixer_info1, np.linspace(-15e6, 10e6, 101), seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
#        plt.close()
    shift_.append(spec.fit_params['freq'].value)
    errors.append(spec.fit_params['freq'].stderr)
    from single_qubit import ssbspec_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    for i in range(1):        
#        RObrick.do_set_power(i)
        seq = sequencer.Trigger(600)
#        seq = Join([seq, qubit2_info.rotate(np.pi/2, X_AXIS)])
        spec = ssbspec_mixer.SSBSpec_mixer(qubit2_info, mixer_info1, np.linspace(-15e6, 10e6, 101), seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
    base_.append(spec.center)
    
    from single_cavity import rocavspectroscopy_keysight_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
#    mixer1_amp = 0.7
#    mixer_info1_set.set_pi_amp(mixer1_amp)
#    
#    mixer_info1 = mclient.get_qubit_info('mixer_info1')
#    mixer_info2 = mclient.get_qubit_info('mixer_info2')
    
    rofreq = 10.810e9
    freq_range = 10e6
    ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit2_info, mixer_info1, np.linspace(10,10,1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 401),
                                             qubit_pulse=False, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.close()
    plt.close()
    
    figure_name = ('S31 at %s'%(field))
    
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'g')
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'g')
    
    
    
    ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit2_info, mixer_info1, np.linspace(10,10,1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 401),
                                             qubit_pulse=True, seq=None)#,extra_info=[ef2_info])
    ro.measure()
    plt.figure('amp%s'%(figure_name))
    plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 2 in e')
    plt.figure('phase%s'%(figure_name))
    plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 2 in e')


Stark_shifts = np.array(shift_)-np.array(base_)
    
    
plt.figure()
plt.title('Stark shifts')
plt.xlabel('Fields (T)')
plt.ylabel('Stark shift (MHz)')
plt.plot(fields,Stark_shifts, label = 'Stark_shift')
plt.plot(fields,base_,label = 'Base')
plt.errorbar(fields,shift_,yerr = errors,label = 'Shift')
plt.legend()


