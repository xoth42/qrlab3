# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 12:26:27 2018

@author: wanglab
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

import os
os.chdir(r'c:\qrlab')

alz = mclient.instruments['alazar']

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')

ge = mclient.instruments['qubit1ge']
ef = mclient.instruments['qubit1ef']

#Yoko = mclient.instruments['Yoko']
qbrick = mclient.instruments['qbrick']
RObrick = mclient.instruments['RObrick']
refbrick = mclient.instruments['refbrick']
AWG2 = mclient.instruments['AWG2']

#Yoko.do_set_current(1.0031e-3)
AWG2.do_set_offset(0, 1)
AWG2.do_set_amplitude(0.026, 1)
qbrick.set_frequency(5158.1e6)
RObrick.set_frequency(8300.8e6)
refbrick.set_frequency(8300.8e6+50e6)
ef.set('deltaf', -375.06e6)
ge.set('pi_amp', 0.293322)
alz.set_naverages(1000)

if 1: #Testing coil response time
    from scripts.single_qubit import coil_response_time
    cr = coil_response_time.CoilResponse(qubit_info, np.array([100e3, 500e3, 1e6, 5e6, 10e6]))
    cr.measure()

if 0: # T1_FT1
    from scripts.single_qubit import T1measurement, FT1measurement, T1_FT1measurement, ssbspec, T1_FT1measurement_justT1andeq, T1_FT1measurement_justFT1andf
    alz.set_naverages(2000)


    for i in range(20):
        
        
        print '###############'
        print i
        print '##############'
#        t1_ft1_justT1 = T1_FT1measurement_justT1andeq.T1_FT1_fluxmeasurementI(qubit_info, ef_info, 6.5e3, 4.5e3, histogram=True, generate=True)
#        t1_ft1_justT1.measure()
        
        seq = sequencer.Trigger(250)
        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 5e6, 101), seq=seq, plot_seqs=False)
        spec.measure()
        
        #Yoko.do_set_current(0)
        AWG2.do_set_offset(0, 1)
        qbrick.set_frequency(5435e6)
        RObrick.set_frequency(8302e6)
        refbrick.set_frequency(8302e6+50e6)
        time.sleep(1)
        ge.set('pi_amp', 0.278468)
        
        
#        t1_ft1_justFT1 = T1_FT1measurement_justFT1andf.T1_FT1_fluxmeasurementII(qubit_info, ef_info, 6.5e3, 4.5e3, histogram=True, generate=True)
#        t1_ft1_justFT1.measure()
        
        seq = sequencer.Trigger(250)
        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 5e6, 101), seq=seq, plot_seqs=False)
        spec.measure()
        
#        seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
#        postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#        spec = ssbspec.SSBSpec(ef_info, np.linspace(-5e6, 5e6, 51), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True)
#        spec.measure()
        
        #Yoko.do_set_current(1.0031e-3)
        AWG2.do_set_offset(0.026, 1)
        qbrick.set_frequency(5158.1e6)
        RObrick.set_frequency(8300.8e6)
        refbrick.set_frequency(8300.8e6+50e6)
        time.sleep(1)
        ge.set('pi_amp', 0.292872)
        
        #plt.close('all')