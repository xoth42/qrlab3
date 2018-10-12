# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 14:53:09 2018

@author: wanglab
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


qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')

if 0:
    dig = mclient.instruments['dig']
    data = dig.test_dig(1000, 1, 1, 1)
    print(np.shape(data))
    plt.clf()
    plt.plot(data[0][0][:])
    plt.plot(data[1][0][:])
    plt.show()



if 0:
    from single_cavity import rocavspectroscopy_keysight
#    rofreq = 8553.1e6

    rofreq = 7719.07e6
    freq_range = 1e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-4, -40, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 50),
                                             qubit_pulse=False)
    ro.measure()
    
if 0:
    from single_cavity import rocavspectroscopy_keysight_IQmod
#    rofreq = 8553.1e6
    rofreq = 8306.00e6
    freq_range = 15e6
    ro = rocavspectroscopy_keysight_IQmod.ROCavSpectroscopy(qubit_info, RO_info, np.linspace(-10, -20, 3),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 55),
                                             plen=20000, amp=0.0001, qubit_pulse=False)
    ro.measure()
    

if 0:
    from single_qubit import spectroscopy_keysight
#    from scripts.single_qubit import spectroscopy_IQ
#    for i in range(5560, 5560, 0):
    qubit_freq = 4534.13e6
    freq_range = 1.5e6
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['geBrick'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 251),
                                     [-30],
                                     plen=5000, amp=0.006, plot_seqs=False) 

    spec.measure()

    
    
    
if 0:
    from scripts.single_qubit import ssbspec
    seq = sequencer.Trigger(250)

    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-1e6, 1e6, 50), seq=seq, plot_seqs=False)
    spec.measure_keysight()
    bla
    
    
if 0: # Calibrate pi pulse
    from scripts.single_qubit import rabi
    tr = rabi.Rabi(qubit_info, 
#                   np.linspace(-.06, .06, 100), selective=True,
                   np.linspace(-.3, .3, 150), selective=False,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False)
    tr.measure_keysight()
    
    bla
    
    
if 0: # T1
    from scripts.single_qubit import T1measurement

    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 200e3, 151), 
                                     double_exp=False, generate=True, plot_seqs=False)
    t1.measure_keysight()
    bla
    



if 1:
    from scripts.single_qubit import ssbspec
    from scripts.single_qubit import rabi
    from scripts.single_qubit import T1measurement
    powers = np.linspace(-20, 10, 2)
    frequencies = np.linspace(120, 180, 3)
    
    driveFG = mclient.instruments['aliceFG']
    dig = mclient.instruments['dig']
    geFG = mclient.instruments['geFG']
    normal_ge = 4534050000.0
    dig.set_naverages(2000)
    
    freq_arr = np.zeros_like(powers)
    T1_arr = np.zeros_like(powers)
    
    for i in range(len(powers)):
        geFG.set_frequency(normal_ge)
        driveFG.set_power(powers[i])
        seq = sequencer.Trigger(250)
        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-15e6, 1e6, 150), seq=seq, plot_seqs=False)
        spec.measure_keysight()
        freqs = spec.xs
        ys = spec.get_ys()
        geFG.set_frequency(geFG.get_frequency() + freqs[np.argmin(ys)])
        
        tr = rabi.Rabi(qubit_info, 
                   np.linspace(-.3, .3, 150), selective=False,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=True)
        tr.measure_keysight()
        
        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 200e3, 150), 
                                     double_exp=False, generate=True, plot_seqs=False)
        t1.measure_keysight()
        
        freq_arr[i] = freqs[np.argmin(ys)]
        T1_arr[i] = t1.analyze()
        
    plt.clf()
    plt.plot(powers, T1_arr)
    plt.show()
    
    
if 0: # EF SSBspec
    from scripts.single_qubit import ssbspec
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-10e6, 10e6, 101), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True)
    spec.measure_keysight()
    bla

if 0: # EF rabi -ef_info not defined
    from scripts.single_qubit import efrabi
#    alz.set_naverages(2000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.1, 0.1, 101), plot_seqs=False, selective=False, generate=True)
    efr.measure_keysight()
#    period = efr.fit_params['period'].value
#    alz.set_naverages(4000)
#    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.01, 0.01, 51), first_pi=False, selective=True, force_period=period, generate=True)
#    efr.measure_keysight()
#    alz.set_naverages(2000)
    bla
    