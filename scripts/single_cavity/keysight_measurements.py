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
#RO_info = mclient.get_qubit_info('RO')
os.chdir(r'C:/qrlab/scripts')

if 0:
    from single_cavity import rocavspectroscopy_keysight
#    rofreq = 8553.1e6
    rofreq = 8306.00e6
    freq_range = 15e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy(qubit_info, np.linspace(-20, -20, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 61),
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
    from single_qubit import rabi_keysight
    tr = rabi_keysight.Rabi_Keysight(qubit_info, np.linspace(.3, 0, 5), plot_seqs=False, generate=True, 
                                     selective=False, repeat_pulse=1, update=False)
    data=tr.measure_keysight()
    
if 1:
    from single_qubit import spectroscopy_keysight
#    from scripts.single_qubit import spectroscopy_IQ
#    for i in range(5560, 5560, 0):
    qubit_freq = 6000e6
    freq_range = 100e6
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['qbrick'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,

                                                 qubit_freq+freq_range, 251),
                                     [-20],
                                     plen=20000, amp=0.0001, plot_seqs=False) 

    spec.measure()

    bla