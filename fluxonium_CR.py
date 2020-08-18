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
qubit_info3 = mclient.get_qubit_info('qubit3ge')
gate_info1 = mclient.get_gate_info('sq_gate1')
gate_info2 = mclient.get_gate_info('sq_gate2')
#zx90_info = mclient.get_gate_info('zx90_gate')
cx_info = mclient.get_gate_info('cx_gate')
cancel_info = mclient.get_gate_info('cancel_gate')
ZZ_info = mclient.get_gate_info('ZZ_info')
offset_info = mclient.get_qubit_info('offset_info')

from scripts.single_qubit import ssbspec
from scripts.single_qubit import ssbspec_gaussianfit

from scripts.single_qubit import rabi
from scripts.single_qubit import drag_test
from scripts.fluxonium  import timerabi_interleaved
from scripts.fluxonium import CRtuning_time_phase
from scripts.fluxonium import CRtuning_time_amp
from scripts.single_qubit import timerabi
from scripts.fluxonium import CRtuning_timevsdet
from scripts.single_qubit import geophasecal_zx90


cool = sequencer.Constant(int(4e3),1,chan='3m1')
seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

rotation = 0
X_proj = gate_info1.rotate(np.pi/2, np.pi/2+rotation)
Y_proj = gate_info1.rotate(np.pi/2, rotation)
    
def Drag_test(qubit_info):   
    dtest = drag_test.drag_test(qubit_info, np.linspace(0, 2.0, 51), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()

def qubit2_gate_check(amp, range, qubit1):
    alz.set_naverages(5000)
    rel_amp=0
    rel_phase = 0
    tr = timerabi_interleaved.TimeRabi_interleaved(
            gate_info2, qubit1, range, #Does not include Gaussian ramp time, sigma=4
            amp, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=6,
            update=False, seq=seq_cool, postseq=None, proj_func='phase')
    data = tr.measure()
    return

def morning_check():
    if 0: #Check ZZ -- SSB for upper qubit with ZZ for lower qubit in g vs e
        spec1 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-4e6, 4e6, 81), proj_func='phase', seq=seq_cool)
        spec1.measure()
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi,0)])
        spec1 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-4e6, 4e6, 81), proj_func='phase', seq=seq, extra_info=qubit2_info)
        spec1.measure()    

    from scripts.fluxonium import ssbspec_gaussianfit_ZZon
    if 0: #Check ZZ -- SSB for upper qubit with ZZ for lower qubit in g vs e
        spec1 = ssbspec_gaussianfit_ZZon.SSBSpec_Gaussianfit(qubit_info, offset_info, np.linspace(-15e6, 15e6, 81), proj_func='phase', seq=seq_cool)
        spec1.measure()
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi,0)])
        spec1 = ssbspec_gaussianfit_ZZon.SSBSpec_Gaussianfit(qubit_info, offset_info, np.linspace(-15e6, 15e6, 81), proj_func='phase', seq=seq, extra_info=qubit2_info)
        spec1.measure()    






    
    if 0: #Check population after cooling:
        ZZ.set_rf_on(False)
        spec2 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-5e6,5e6, 81), proj_func='phase', seq=seq_cool)
        spec2.measure()
        spec2 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, np.linspace(-5e6, 5e6, 81), proj_func='phase', seq=seq_cool)
        spec2.measure()   
        ZZ.set_rf_on(True)
    
    if 0: #Rabi checking pi amps for upper qubit from both input lines
        tr1 = rabi.Rabi(qubit_info, np.linspace(-0.2, 0.2, 61), selective=False,
                                       plot_seqs=False, generate=True, repeat_pulse=1,
                                       update=True, seq=seq_cool, postseq=None, proj_func='phase')
        data=tr1.measure()
        tr1 = rabi.Rabi(qubit_info2, np.linspace(-0.5, 0.5, 61), selective=False,
                                       plot_seqs=False, generate=True, repeat_pulse=1,
                                       update=True, seq=seq_cool, postseq=None, proj_func='phase')
        data=tr1.measure()
    
    if 0: #Rabi checking pi amps for lower qubit from both input lines
        tr2 = rabi.Rabi(qubit2_info, np.linspace(-0.2, 0.2, 61), selective=False,
                                       plot_seqs=False, generate=True, repeat_pulse=1,
                                       update=True, seq=seq_cool, postseq=None, proj_func='phase')
        data=tr2.measure()    
        tr2 = rabi.Rabi(qubit2_info2, np.linspace(-0.5, 0.5, 61), selective=False,
                                       plot_seqs=False, generate=True, repeat_pulse=1,
                                       update=True, seq=seq_cool, postseq=None, proj_func='phase')
        data=tr2.measure()  

    if 0: #Check coherence
        from scripts.single_qubit import T2measurement
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                         proj_func='phase', seq=seq_cool)
        t2.measure()
        t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                         proj_func='phase', seq=seq_cool)
        t2.measure()
    return


def relative_phase_qubit1(amp, rel_amp, timerange, phase_range, control_pi=False):
    cr_tune = CRtuning_time_phase.CRtuning_time_phase(qubit_info, qubit_info2, qubit2_info2, 
                                                    timerange, phase_range, 
                amp=amp, phase=0, rel_amp=rel_amp, sigma=4, seq=seq_cool, postseq=None, 
                control_pi=False, proj_func='phase')#,extra_info=gate_info1)    
    data = cr_tune.measure()
    return


def relative_amp_qubit1(amp, rel_phase, timerange, amp_range, control_pi=False):
    cr_tune = CRtuning_time_amp.CRtuning_time_amp(qubit_info, qubit_info2, qubit2_info2, 
                                                    timerange, amp_range, 
                amp=amp, phase=0, rel_phase=1, sigma=4, seq=seq_cool, postseq=None, 
                control_pi=False, proj_func='phase', extra_info=gate_info1)    
    data = cr_tune.measure()
    return


def detuning_qubit1(amp,rel_amp,  rel_phase, time_range, det_range, control_pi=True):
    cr_tune = CRtuning_timevsdet.CRtuning_timevsdet(qubit_info, qubit_info2, qubit2_info2, 
                                                    time_range, det_range, 
                amp, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=4, update=False, 
                seq=seq_cool, fix_phase=True, fix_period=None, control_pi=True, proj_func='phase')    
    
    data = cr_tune.measure()
    return


def CX_timerabis(rotation_range, gate_info1, gate_info2, time_range, amp, rel_amp,rel_phase, all_axis=False, repeat_pulse=1):
    alz.set_naverages(1000)
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
    for R in rotation_range:
        X_proj = gate_info1.rotate(np.pi/2, np.pi/2+R)
        Y_proj = gate_info1.rotate(np.pi/2, R)
        if all_axis== False:
            for postseq in [None]:
                tr = timerabi_interleaved.TimeRabi_interleaved(
                    gate_info1, gate_info2, time_range, #Does not include Gaussian ramp time, sigma=4
                    amp=amp, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=4,
                    update=False, seq=seq_cool,repeat_pulse=repeat_pulse, postseq=postseq, proj_func='phase')#,extra_info=gate_info1)
                data = tr.measure()
        if all_axis == True:
            for postseq in [None]:
                tr = timerabi_interleaved.TimeRabi_interleaved(
                    gate_info1, gate_info2, time_range, #Does not include Gaussian ramp time, sigma=4
                    amp=amp, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=4,
                    update=False, seq=seq_cool, repeat_pulse=repeat_pulse, postseq=postseq, proj_func='phase')#,extra_info=gate_info1)
                data = tr.measure()
    return         

def qubit1_gate_check(amp, rel_amp, rel_phase):

    tr = timerabi_interleaved.TimeRabi_interleaved(gate_info1, gate_info2, np.linspace(0, 250,151), #Does not include Gaussian ramp time, sigma=4
            amp=0.079, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=4,
            update=False, seq=seq_cool, postseq=None, proj_func='phase')
    data = tr.measure()
    return


def zx_amplitude(gate_info, range, repeat_pulse):
    alz.set_naverages(5000)
    tr1 = rabi.Rabi(zx90_info, np.linspace(-0.15, 0.15, 101), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=repeat_pulse,
                                   update=False, seq=seq_cool, postseq=None, proj_func='phase',
#                                   extra_info=gate_info2
                                   )
    data=tr1.measure()    
    bla


def phase_shift_check(repeat_pulse):
#    alz.set_naverages(3000)

    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])  
#    postseq = gate_info1.rotate(np.pi, 0)
    geoph = geophasecal_zx90.geophasecal(gate_info2, zx90_info, gate_info1, np.linspace(-3, 3, 61), repeat_pulse=repeat_pulse,
                                    seq=seq, postseq=None, proj_func='phase'
                                    )
    data=geoph.measure()    
    return 
    




#------------------------------------------------------------------------------------

if 0:
    morning_check()
    bla

if 0:  #for qubit2: checking how good is a single qubit drive from a direct drive from 9,10
    qubit2_gate_check(0.3, np.linspace(0, 300, 151), gate_info1)

    bla


if 0: # CX tune up
#    relative_phase_qubit1(0.079, 4.457, np.linspace(1,300,31), np.linspace(0.97,1.03,11), control_pi=False)

#    relative_amp_qubit1(0.079, 1.004,  np.linspace(1,300,31), np.linspace(4.35,4.55,11), control_pi=False)
    CX_timerabis(np.linspace(-0.8,-0.8,1), gate_info1, gate_info2 ,np.linspace(0,250,101), 0.079, 4.452, 1.004, all_axis=False)
    bla

if 0: #single qubit gate tune up for qubit1
    detuning_qubit1(0.079,4.452, 1.004, np.linspace(0,300,31),np.linspace(-5e6, 5e6, 11) , control_pi=True)
    #driving from 5/6 with control in g and e:
    CX_timerabis(np.linspace(-0.8,-0.8,1), qubit_info, qubit_info2, qubit2_info2 ,np.linspace(0,300,151), 0.079, 0.000, 0, all_axis=False)
    #driving from 5/6 with control in g and e:
    CX_timerabis(np.linspace(-0.8,-0.8,1), qubit_info2, qubit_info, qubit2_info2,np.linspace(0,300,151), 0.3627, 0.000, 0, all_axis=False)
    #calculation will go in here
    qubit1_gate_check(0.79, 1.015, 1.004)

if 0: #ZX90_Echo tune up
    CX_timerabis(np.linspace(0.0, 0.0, 1), gate_info1, gate_info2, np.linspace(0,300,101), 0.078, 4.452, 1.004, repeat_pulse=2, all_axis=True)
#    zx_amplitude(zx90_info, np.linspace(-0.15,0.15,101), repeat_pulse=2)

if 0:    #phase_shift_check
    phase_shift_check(2)
    bla


if 0:
    Drag_test(gate_info1)
    Drag_test(gate_info2)  


if 0: #Rabi checking pi amp for single qubit gate
    alz.set_naverages(4000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])#, gate_info2.rotate(np.pi,0)])
#                          sequencer.Combined([cx_info.rotate(np.pi, 0), cancel_info.rotate(np.pi, 0)])])
#                          sequencer.Combined([cx_info.rotate(np.pi, 0), cancel_info.rotate(np.pi, 0)])
#    postseq =  gate_info2.rotate(np.pi,0)
    tr1 = rabi.Rabi(gate_info2, np.linspace(-0.4,0.4, 101), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1, cancel_info=None,
                                   update=False, seq=seq, postseq=None, proj_func='phase',
                                   extra_info=gate_info2,
                                   )
    data=tr1.measure()    
    bla

if 0: # Time Rabi
    from scripts.single_qubit import timerabi
    alz.set_naverages(8000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])#, gate_info1.rotate(np.pi*1.0000,0)])    
#    postseq =  gate_info1.rotate(np.pi,0)
    tr = timerabi.TimeRabi(cancel_info, np.linspace(0, 60, 61), amp=0.10, 
                           seq=seq_cool, postseq=None, plot_seqs=False, proj_func='phase')#, extra_info=gate_info1)
    data = tr.measure()
    bla




    
if 0: # Tune up for time vs relative amp
    rotation = 0.0
    X_proj = gate_info1.rotate(np.pi/2, np.pi/2+rotation)
    Y_proj = gate_info1.rotate(np.pi/2, rotation)
    
    cr_tune = CRtuning_time_amp.CRtuning_time_amp(gate_info1, gate_info2,  
                                                    np.linspace(1,400,21), rel_amps=np.linspace(4.4,4.8,21), 
                amp=0.079849, phase=0, rel_phase=-0.433, sigma=6, seq=seq_cool, postseq=None, cancel_info=None,
                control_pi=False, proj_func='phase', extra_info=gate_info1)    
    data = cr_tune.measure()
    bla
    
if 0: # Tune up for time vs relative phase
    alz.set_naverages(1250)
#    rotation = 0.0
#    X_proj = gate_info1.rotate(np.pi/2, np.pi/2+rotation)
#    Y_proj = gate_info1.rotate(np.pi/2, rotation)

    cr_tune = CRtuning_time_phase.CRtuning_time_phase(gate_info1, gate_info2,  
                                                    np.linspace(1,400,21), rel_phases=np.linspace(-0.5,-0.35,21), 
                amp=0.079849, phase=0, rel_amp=4.66, sigma=6, seq=seq_cool, postseq=None, cancel_info=None,
                control_pi=False, proj_func='phase',plot_seqs=False)    
    data = cr_tune.measure()
    bla


if 0: # Tune up for time vs detuning   
    
    from scripts.fluxonium import CRtuning_timevsdet
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
    cr_tune = CRtuning_timevsdet.CRtuning_timevsdet(qubit_info, qubit_info2, qubit2_info2, 
                                                    np.linspace(0,100,31), np.linspace(0e6, 50e6, 11), 
                amp=0.3, phase=0, rel_amp=0, rel_phase=0.9891, sigma=4, update=False, 
                seq=seq_cool, fix_phase=True, fix_period=None, control_pi=False, proj_func='phase')    
    
    data = cr_tune.measure()
    bla
    
if 0: # Tune up 1Q gates with Interleaved Time Rabi
    from scripts.fluxonium  import timerabi_interleaved
    alz.set_naverages(5000)
#    rotation = 0.6
#    X_proj = qubit2_info.rotate(np.pi/2, np.pi/2+rotation)
#    Y_proj = qubit2_info.rotate(np.pi/2, rotation)
    rel_amp=0.0000000001
    rel_phase = 0
#    rel_phase = 1.77#-np.pi
    for postseq in [None]:
        tr = timerabi_interleaved.TimeRabi_interleaved(
            gate_info2, gate_info1, np.linspace(0, 100, 81), #Does not include Gaussian ramp time, sigma=4
            amp=0.35, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=6,
            update=False, seq=seq_cool, postseq=postseq, proj_func='phase', read_on_e=False)
        data = tr.measure()
    bla
        
if 0: # Tune up CR with Interleaved Time Rabi
    from scripts.fluxonium  import timerabi_interleaved
    alz.set_naverages(2000)
#    controlpi = gate_info2.rotate(np.pi, 0)
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
#    rotation = -0.08
    rotation = 0
    X_proj = gate_info1.rotate(np.pi/2, np.pi/2+rotation)
    Y_proj = gate_info1.rotate(np.pi/2, rotation)
    for rel_amp in [4.667]:
#    rel_amp= 4.457#5.03#4.4493
        for rel_phase in [-0.442]: #1.011
#    rel_amp=4.4405
#    rel_phase=1.01
            
            for postseq in [None]:
                tr = timerabi_interleaved.TimeRabi_interleaved(
                            gate_info1, gate_info2, np.linspace(0, 300, 151), #Does not include Gaussian ramp time, sigma=4
                            amp=0.079849, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=6, read_on_e=True, cancel_info=None, 
                            update=False, seq=seq_cool, postseq=None, proj_func='phase', plot_seqs=False, extra_info=None)
                data = tr.measure()
        
if 0: #Calibration of the CR-imprinted phase for control qubit in |g>
    from scripts.single_qubit import geophasecal
    alz.set_naverages(3000)

    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])  
    postseq = gate_info1.rotate(np.pi, 0)
    geoph = geophasecal.geophasecal(gate_info2, cx_info, np.linspace(-np.pi, np.pi, 61), test_info2=cancel_info, repeat_pulse=2,
                                    seq=seq, postseq=None, proj_func='phase', plot_seqs=False,
#                                    extra_info=gate_info1
                                    )
    data=geoph.measure()    
    bla
    
        

if 0: # single qubit tune up for time vs relative amp for  #NEED TO FIX THE 2D PLOTTING ISSUE
    from scripts.fluxonium import Singlequbit_tuning_time_amp
    sq_tune = Singlequbit_tuning_time_amp.Singlequbit_tuning_time_amp(qubit_info, qubit_info2, gate_info2, 
                                                    np.linspace(1,200,21), rel_amps=np.linspace(4,5.0,9), 
                amp=0.08, phase=0, rel_phase=-1.07, sigma=6, seq=seq_cool, proj_func='phase')    
    data = sq_tune.measure()

if 0: # Single qubit tune up for time vs relative phase  
    from scripts.fluxonium import Singlequbit_tuning_time_phase
    sq_tune = Singlequbit_tuning_time_phase.Singlequbit_tuning_time_phase(qubit_info, qubit_info2, qubit2_info, 
                                                    np.linspace(1,100,15), rel_phases=np.linspace(-0.5*np.pi,0.5*np.pi,11), 
                amp=0.05, phase=0, rel_amp=1, sigma=5, seq=seq_cool, proj_func='phase')    
    data = sq_tune.measure()

#if 0: # single qubit tune up for time vs relative amp for  #NEED TO FIX THE 2D PLOTTING ISSUE
#    from scripts.fluxonium import Singlequbit_tuning_powerrabi
#    sq_tune = Singlequbit_tuning_powerrabi.Singlequbit_tuning_powerrabi(qubit_info2, qubit_info, qubit2_info, 
#                                                  np.linspace(-0.1,0.1,11), np.linspace(0,0.5,15), seq=seq_cool, proj_func='phase')    
#    data = sq_tune.measure()


#if 1: #trying zx90 tomo
#    from scripts.fluxonium import zx90_tomo
#    alz.set_naverages(6000)
#
#    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])  
#    zx = zx90_tomo.zx90_tomo(gate_info2, gate_info1, zx90_info, 
#                                    seq=seq,proj_func='phase') 
#                                    
#                                    
#    data=zx.measure()    
#    bla


if 1: # Tune up for time vs detuning  #ebru - have not been troughly tested 
    
    from scripts.fluxonium import cphase_zztune
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
    cr_tune = cphase_zztune.cphase_zztune(ZZ_info, offset_info, qubit_info, qubit2_info,
                                                    np.linspace(0,600,11), np.linspace(10e6, 45e6,21), 
                amp=0.15, phase=0, sigma=4, update=False, 
                seq=seq_cool, fix_phase=True, fix_period=None,proj_func='phase')    
    
    data = cr_tune.measure()
    bla


if 0: # 
    from scripts.fluxonium  import CZ_1Dseq
    alz.set_naverages(10000)

    cz = CZ_1Dseq.TimeRabi_interleaved(
                            gate_info1, gate_info2, offset_info, np.linspace(0, 1000,51), #Does not include Gaussian ramp time, sigma=4
                            read_on_e=False,  
                            update=False, seq=seq_cool, postseq=None, proj_func='phase', plot_seqs=False, extra_info=None)
    data = cz.measure()
