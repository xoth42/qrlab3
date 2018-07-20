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
os.chdir(r'C:/qrlab/scripts')

if 0:
    from single_cavity import rocavspectroscopy_keysight
#    rofreq = 8553.1e6
    rofreq = 8307.00e6
    freq_range = 5e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy(qubit_info, np.linspace(-12, -18, 3),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 40),
                                             qubit_pulse=False)
    ro.measure()
    
if 0:
    from single_qubit import rabi_keysight
    tr = rabi_keysight.Rabi_Keysight(qubit_info, np.linspace(.3, 0, 5), plot_seqs=False, generate=True, 
                                     selective=False, repeat_pulse=1, update=False)
    data=tr.measure_keysight()
    
if 1:
    from single_qubit import spectroscopy_keysight
#    from scripts.single_qubit import spectroscopy_IQ
    qubit_freq = 5938.00e6
    freq_range = 50e6
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['qbrick'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,

                                                 qubit_freq+freq_range, 100),
                                     [-15],
                                     plen=20000, amp=0.1, plot_seqs=False) #1=1ns

#    spec = spectroscopy_IQ.Spectroscopy_IQ(client.instruments['gen'], qubit_info,
#                                     np.linspace(702e6, 710e6, 81), [-30],
#                                    plen=250*100, amp=0.1, ssb=False, plot_seqs=False)

    spec.measure()
    bla