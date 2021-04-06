# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 11:27:55 2020

@author: wanglab
"""
import mclient
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
import matplotlib.pyplot as plt
import math 
import time
import lmfit


import os
os.chdir(r'c:\qrlab')

alz = mclient.instruments['alazar']
yoko = mclient.instruments['yoko']
gaius01 = mclient.instruments['gaius01']
coolgen= mclient.instruments['cool']
ZZ = mclient.instruments['ZZ']

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
efinfo = mclient.get_qubit_info('efinfo')
gate_info1 = mclient.get_gate_info('sq_gate1')
gate_info2 = mclient.get_gate_info('sq_gate2')
ZZ_info = mclient.get_gate_info('ZZ_gate')


#ef_info = mclient.get_qubit_info('qubit1ef')
qubit2_info = mclient.get_qubit_info('qubit2ge')
qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')
#f0g1 cooling parameters



if 0: # EF SSBspec
    from scripts.single_qubit import ssbspec
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150),  gate_info2.rotate(np.pi,0)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150),  gate_info1.rotate(np.pi,0)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])# qubit2_info.rotate(np.pi, 0)])
#    for postseq in [None, sequencer.Join([gate_info1.rotate(np.pi,0)]), sequencer.Join([gate_info2.rotate(np.pi,0)]), sequencer.Join([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])]:
    postseq = sequencer.Join([gate_info2.rotate(np.pi,0)])
#    postseq = sequencer.Combined([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])
    spec = ssbspec.SSBSpec(efinfo, np.linspace(-10e6, 10e6, 101), seq=seq, postseq = postseq, extra_info=[gate_info2, gate_info1], plot_seqs=False, generate=True, proj_func='phase')
    spec.measure()
    bla


if 0: # Time Rabi
    from scripts.single_qubit import timerabi
    alz.set_naverages(20000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])   
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0)])    
    postseq =  gate_info1.rotate(np.pi,0)
#    postseq =  sequencer.Combined([gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])
    tr = timerabi.TimeRabi(efinfo, np.linspace(0, 100, 101), amp=0.145, 
                           seq=seq_cool, postseq=postseq, proj_func='phase', plot_seqs=False, extra_info=[gate_info1, gate_info2])
    data = tr.measure()
    bla



if 0: #2d time amp vs detuning 
    from scripts.fluxonium import Timerabi_det_2D
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])   
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0)])    
    postseq =  gate_info1.rotate(np.pi,0)
    timerabi_det = Timerabi_det_2D.Timerabi_det_2D(efinfo, np.linspace(0, 40, 21), np.linspace(-80e6,-30e6,15), amp=0.08,  
               sigma=4, seq=seq_cool, postseq=postseq, 
                control_pi=False, proj_func='phase', extra_info=[gate_info1, gate_info2])    
    data = timerabi_det.measure()
    bla


if 0:    #Power rabi
    from scripts.single_qubit import rabi

    for i in range(1):
        cool = sequencer.Constant(int(4e3),1,chan='3m1')
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), sequencer.Combined([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)]), qubit_info3.rotate(np.pi,0)])# qubit2_info.rotate(np.pi, 0)])
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#        postseq = sequencer.Join([gate_info1.rotate(np.pi,0)])
        postseq = sequencer.Combined([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])
        tr = rabi.Rabi(efinfo, np.linspace(-0.05, 0.05, 81), selective=False,
                #                   np.linspace(0.75, 0.95, 101), selective=False,
                #                           np.linspace(-0.2, 0.2, 61), selective=True,
                                   plot_seqs=False, generate=True, repeat_pulse=1,  #n=3 has a bug
                                   update=True, seq=seq,
                                   postseq=postseq, proj_func='phase', extra_info=[gate_info1, gate_info2])
        data=tr.measure()

    
    bla   
    
if 0: # T2
    from scripts.single_qubit import T2measurement
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0)
    postseq = sequencer.Combined([gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])
    if 1:
#        coolgen.set_rf_on(True)
#    
    #    for i in range(1):
        t2 = T2measurement.T2Measurement(efinfo, np.linspace(0, 0.5e3, 81), detune=4e6, double_freq=False, 
                                         generate=True, postseq=postseq, extra_info =[gate_info1, gate_info2],
                                             proj_func='phase', seq=seq)
        t2.measure()
        bla

if 1: # T2echo
    from scripts.single_qubit import T2measurement
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0)
    postseq = sequencer.Combined([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])
#    alz.set_naverages(7000)
    t2 = T2measurement.T2Measurement(efinfo, np.linspace(10, 1.5e3, 101), detune=3e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     seq=seq, postseq=postseq, extra_info =[gate_info1, gate_info2], proj_func='phase')
    t2.measure()
    bla
