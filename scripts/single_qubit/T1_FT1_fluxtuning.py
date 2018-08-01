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

Yoko = mclient.instruments['Yoko']
qbrick = mclient.instruments['qbrick']
RObrick = mclient.instruments['RObrick']
refbrick = mclient.instruments['refbrick']

Yoko.do_set_current(.00069225)
qbrick.set_frequency(5670.1e6)
RObrick.set_frequency(8305.4e6)
refbrick.set_frequency(8305.4e6+50e6)
ef.set('deltaf', -370.5e6)

if 1: # T1_FT1
    from scripts.single_qubit import T1measurement, FT1measurement, T1_FT1measurement, ssbspec, T1_FT1measurement_justT1andeq, T1_FT1measurement_justFT1andf
    alz.set_naverages(1000)


    for i in range(10000):
        
        
        print '###############'
        print i
        print '##############'
        t1_ft1_justT1 = T1_FT1measurement_justT1andeq.T1_FT1_fluxmeasurementI(qubit_info, ef_info, 6e3, 5e3, keep_shots=False, generate=True)
        t1_ft1_justT1.measure()
        
#        seq = sequencer.Trigger(250)
#        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 5e6, 51), seq=seq, plot_seqs=False)
#        spec.measure()
        
        Yoko.do_set_current(0.00002)
        qbrick.set_frequency(5943.822e6)
        RObrick.set_frequency(8306.75e6)
        refbrick.set_frequency(8306.75e6+50e6)
        time.sleep(0.2)
        
        
        t1_ft1_justFT1 = T1_FT1measurement_justFT1andf.T1_FT1_fluxmeasurementII(qubit_info, ef_info, 6e3, 5e3, keep_shots=False, generate=True)
        t1_ft1_justFT1.measure()
        
#        seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
#        postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#        spec = ssbspec.SSBSpec(ef_info, np.linspace(-5e6, 5e6, 51), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True)
#        spec.measure()
        
        Yoko.do_set_current(.00069225)
        qbrick.set_frequency(5670.1e6)
        RObrick.set_frequency(8305.4e6)
        refbrick.set_frequency(8305.4e6+50e6)
        time.sleep(0.2)
        
        plt.close('all')