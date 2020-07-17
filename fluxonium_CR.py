# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 11:48:14 2020

@author: wanglab
"""

import mclient
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib.pyplot as plt
import os
os.chdir(r'c:\qrlab')

alz = mclient.instruments['alazar']
gaius01 = mclient.instruments['gaius01']
coolgen= mclient.instruments['cool']
ZZ = mclient.instruments['ZZ']

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
qubit2_info = mclient.get_qubit_info('qubit2ge')
qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')

from scripts.single_qubit import ssbspec
from scripts.single_qubit import ssbspec_gaussianfit

from scripts.single_qubit import rabi

cool = sequencer.Constant(int(8e3),1,chan='3m1')
seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])





if 0: #Check ZZ -- SSB for upper qubit with ZZ for lower qubit in g vs e
    spec1 = ssbspec.SSBSpec(qubit_info, np.linspace(-4e6, 4e6, 81), proj_func='phase', seq=seq_cool)
    spec1.measure()
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi,0)])
    spec1 = ssbspec.SSBSpec(qubit_info, np.linspace(-4e6, 4e6, 81), proj_func='phase', seq=seq, extra_info=qubit2_info)
    spec1.measure()    
    
if 0: #Check population after cooling:
    ZZ.set_rf_on(False)
    spec2 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-15e6,8e6, 81), proj_func='phase', seq=seq_cool)
    spec2.measure()
#    spec2 = ssbspec.SSBSpec(qubit2_info, np.linspace(-3e6, 3e6, 81), proj_func='phase', seq=seq_cool)
#    spec2.measure()   
    ZZ.set_rf_on(True)
    
if 1: #Rabi checking pi amps for upper qubit from both input lines
    tr1 = rabi.Rabi(qubit_info, np.linspace(-0.2, 0.2, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
    data=tr1.measure()
    tr1 = rabi.Rabi(qubit_info2, np.linspace(-0.4, 0.4, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
    data=tr1.measure()
    
if 0: #Rabi checking pi amps for lower qubit from both input lines
    tr2 = rabi.Rabi(qubit2_info, np.linspace(-0.2, 0.2, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
    data=tr2.measure()    
#    tr2 = rabi.Rabi(qubit2_info2, np.linspace(-0.4, 0.4, 61), selective=False,
#                                   plot_seqs=False, generate=True, repeat_pulse=1,
#                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
#    data=tr2.measure()  

if 0: #Check coherence
    from scripts.single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    
    
if 0: # Tune up for time vs relative amp
    from scripts.fluxonium import CRtuning_time_amp
    cr_tune = CRtuning_time_amp.CRtuning_time_amp(qubit_info2, qubit_info, qubit2_info, 
                                                    np.linspace(1,300,31), rel_amps=np.linspace(0.19,0.22,9), 
                amp=0.3, phase=0, rel_phase=0.53, sigma=5, seq=seq_cool, control_pi=False, proj_func='phase')    
    data = cr_tune.measure()
    bla
if 0: # Tune up for time vs relative phase
    from scripts.fluxonium import CRtuning_time_phase
    cr_tune = CRtuning_time_phase.CRtuning_time_phase(qubit_info2, qubit_info, qubit2_info, 
                                                    np.linspace(1,300,31), rel_phases=np.linspace(-0.3,0.3,11), 
                amp=0.3, phase=0, rel_amp=0.203, sigma=5, seq=seq_cool, control_pi=False, proj_func='phase')    
    data = cr_tune.measure()

if 0: # Tune up 1Q gates with Interleaved Time Rabi
    from scripts.fluxonium  import timerabi_interleaved
    alz.set_naverages(5000)
    X_proj = qubit2_info.rotate(np.pi/2, 0)#np.pi*0.30)
    Y_proj = qubit2_info.rotate(np.pi/2, np.pi/2)
    rel_amp=0.0001
    rel_phase = 0.00
    for postseq in [None]:
        tr = timerabi_interleaved.TimeRabi_interleaved(
            qubit2_info2, qubit2_info, qubit_info, np.linspace(0, 240, 81), #Does not include Gaussian ramp time, sigma=4
            amp=0.3, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, 
            update=False, seq=seq_cool, postseq=postseq, proj_func='phase')
        data = tr.measure()
        
if 0: # Tune up CR with Interleaved Time Rabi
    from scripts.fluxonium  import timerabi_interleaved
    alz.set_naverages(5000)
    X_proj = qubit2_info.rotate(np.pi/2, 0)#np.pi*0.30)
    Y_proj = qubit2_info.rotate(np.pi/2, np.pi/2)
    rel_amp=0.203
    rel_phase = 0.53
    for postseq in [None]:
        tr = timerabi_interleaved.TimeRabi_interleaved(
            qubit_info2, qubit_info, qubit2_info, np.linspace(0, 300, 51), #Does not include Gaussian ramp time, sigma=4
            amp=0.3, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, 
            update=False, seq=seq_cool, postseq=postseq, proj_func='phase')
        data = tr.measure()
        
        
if 0: # single qubit tune up for time vs relative amp for  #NEED TO FIX THE 2D PLOTTING ISSUE
    from scripts.fluxonium import Singlequbit_tuning_time_amp
    sq_tune = Singlequbit_tuning_time_amp.Singlequbit_tuning_time_amp(qubit_info, qubit_info2, qubit2_info, 
                                                    np.linspace(1,100,15), rel_amps=np.linspace(0,4,9), 
                amp=0.05, phase=0, rel_phase=0, sigma=5, seq=seq_cool, proj_func='phase')    
    data = sq_tune.measure()

if 0: # Single qubit tune up for time vs relative phase  
    from scripts.fluxonium import Singlequbit_tuning_time_phase
    sq_tune = Singlequbit_tuning_time_phase.Singlequbit_tuning_time_phase(qubit_info, qubit_info2, qubit2_info, 
                                                    np.linspace(1,100,15), rel_phases=np.linspace(-0.5*np.pi,0.5*np.pi,11), 
                amp=0.05, phase=0, rel_amp=1, sigma=5, seq=seq_cool, proj_func='phase')    
    data = sq_tune.measure()


#This is not necessary for the moment
#if 0: # single qubit tune up for time vs relative amp for  #NEED TO FIX THE 2D PLOTTING ISSUE
#    from scripts.fluxonium import Singlequbit_tuning_powerrabi
#    sq_tune = Singlequbit_tuning_powerrabi.Singlequbit_tuning_powerrabi(qubit_info2, qubit_info, qubit2_info, 
#                                                  np.linspace(-0.1,0.1,11), np.linspace(0,0.5,15), seq=seq_cool, proj_func='phase')    
#    data = sq_tune.measure()