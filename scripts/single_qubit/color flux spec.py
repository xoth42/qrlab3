# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 13:37:44 2018

@author: Wang_Lab
"""

import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as plt
from pulseseq import sequencer, pulselib
import matplotlib as mpl
import math as math
import time
import datetime

alz = mclient.instruments['alazar']
#yoko1 = mclient.instruments['yoko1']
dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period=100)
#yoko2 = mclient.instruments['yoko2']
Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB0::11::INSTR')

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
readout_info = mclient.get_readout_info()

#from scripts.single_qubit import spectroscopy_keysight
from scripts.single_qubit import spectroscopy
#from scripts.single_qubit import spectroscopy_phasecorrection

#Make sure to check that repeat is off for Yoko GS200
#To do manually, press 'Program' key and press repeat is the left most option on screen
qubit_freq = 465e6
freq_range1= 50e6
freq_range2 =50e6
freq_points =101
results = []
min_result = []
ramp_currents = np.linspace(-0.55e-3, 0.65e-3, 15) #units are in A
fxn_freq=[]
current = ramp_currents[0]
Yoko.do_set_current(current)




spec = spectroscopy.Spectroscopy(mclient.instruments['QK'], qubit_info,
                                 np.linspace(qubit_freq-freq_range1, qubit_freq+freq_range2, freq_points), [-5],
                                 plen=20000, amp=0.4, plot_seqs=False) #1=1ns


#spec = spectroscopy_phasecorrection.Spectroscopy_phasecorrection(mclient.instruments['sc2'], qubit_info,
#                                 np.linspace(qubit_freq-freq_range1, qubit_freq+freq_range2, freq_points), [5],
#                                 plen=20000, amp=0.001, plot_seqs=False) #1=1ns


#spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['sc2'], qubit_info,
#                                     np.linspace(qubit_freq-freq_range1,
#                                                 qubit_freq+freq_range2, 71),
#                                     [4],
#                                     plen=5000, amp=0.1, plot_seqs=False) 
spec.measure()
phase=np.asarray(spec.phasedata[0,:])
phase=phase[:,None].T
fxn_freq.append(spec.q_freqs[np.argmin(spec.phasedata[0,:])])

for current in ramp_currents[1:]:
    #yoko1.do_set_current(current)
    Yoko.do_set_current(current)
    spec = spectroscopy.Spectroscopy(mclient.instruments['QK'], qubit_info,
                                     np.linspace(qubit_freq-freq_range1, qubit_freq+freq_range2, freq_points), [-5],
                                     plen=20000, amp=0.4, plot_seqs=False) #1=1ns

##
#    spec = spectroscopy_phasecorrection.Spectroscopy_phasecorrection(mclient.instruments['sc2'], qubit_info,
#                                     np.linspace(qubit_freq-freq_range1, qubit_freq+freq_range2, freq_points), [5],
#                                     plen=20000, amp=0.001, plot_seqs=False) #1=1ns
    
    
#    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['sc2'], qubit_info,
#                                     np.linspace(qubit_freq-freq_range1,
#                                                 qubit_freq+freq_range2, 71),
#                                     [4],
#                                     plen=5000, amp=0.1, plot_seqs=False) 
    spec.measure()
    phasenew=np.asarray(spec.phasedata[0,:])
    phasenew=phasenew[:,None].T
    phase= np.concatenate([phase,phasenew])

    fxn_freq.append(spec.q_freqs[np.argmin(spec.phasedata[0,:])])
#print ramp_currents
#print fxn_freq
plt.figure()
#plt.plot(ramp_currents, fxn_freq)
#    results.append(spec.ampdata[0,:])
##    results.append(spec.get_ys())
#    min_result.append(np.min(spec.ampdata[0,:]))
#    plt.close()

X, Y = np.meshgrid(ramp_currents, spec.q_freqs)
X=X*1000
Y=Y/float(1E9)
Z = np.transpose(phase)

#
plt.pcolormesh(X, Y, Z)
plt.colorbar()
plt.xlabel('Coil Current (mA)')
plt.ylabel('Frequency (GHZ)')
plt.show()
to_save = [X, Y, Z]
with file('text.txt','w') as outfile:
    outfile.write('# Array\n')

    # Iterating through a ndimensional array produces slices along
    # the last axis. This is equivalent to data[i,:,:] in this case
    for data_slice in to_save:

        # The formatting string indicates that I'm writing out
        # the values in left-justified columns 7 characters in width
        # with 2 decimal places.
        np.savetxt(outfile, data_slice, fmt='%-7.7f')

        # Writing out a break to indicate different slices...
        outfile.write('# New slice\n')