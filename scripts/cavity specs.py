# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 12:13:51 2019

@author: Wang_Lab
"""
import matplotlib
matplotlib.interactive(True)
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as pl
import time
import objectsharer as objsh
from pulseseq import sequencer, pulselib
import os

qubit_info = mclient.get_qubit_info('qubit1ge')
qubit2_info = mclient.get_qubit_info('qubit2ge')
Magnet = mclient.instruments['Magnet']
readout_info = mclient.get_readout_info('readout')

num = 1
numlist = np.linspace(0,num,num + 1)

freadout = []
for i in numlist:
    from single_cavity import rocavspectroscopy_keysight
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    rofreq = 10.935e9
    freq_range = 2.5e6
    dig.set_naverages(5000)
    SC_qubit.set_rf_on(True)
    qubitbrick.set_rf_on(True)
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-5, 10, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=False, seq=None)
    ro.measure()
    
#by Yingying
    max_freq = ro.freqs[np.argmax(ro.ampdata[0])]
    print max_freq
    readout_info.rfsource1.set_frequency(max_freq)
    readout_info.rfsource2.set_frequency(max_freq+50e6)    

    freadout.append(max_freq)
    
pl.figure()
pl.plot(numlist, np.asarray(freadout)/1e6, label = 'readout freq(MHz)')
pl.legend()
pl.show()
