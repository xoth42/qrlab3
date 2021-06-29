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
#qubit_info3 = mclient.get_qubit_info('qubit3ge')
gate_info1 = mclient.get_gate_info('sq_gate1')
gate_info2 = mclient.get_gate_info('sq_gate2')
#zx90_info = mclient.get_gate_info('zx90_gate')
#cx_info = mclient.get_gate_info('cx_gate')
#cancel_info = mclient.get_gate_info('cancel_gate')
ZZ_info = mclient.get_gate_info('ZZ_gate')
ZZobj = mclient.instruments['ZZ_gate']
#offset_info = mclient.get_qubit_info('offset_info')

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
from scripts.fluxonium import rabi_echo

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
    if 1: #Check ZZ -- SSB for upper qubit with ZZ for lower qubit in g vs e
        spec1 = ssbspec.SSBSpec(qubit_info, np.linspace(-4e6, 3e6, 201), proj_func='phase', seq=seq_cool)
        spec1.measure()
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi,0)])
        spec1 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-4e6, 3e6, 181), proj_func='phase', seq=seq, extra_info=qubit2_info)
        spec1.measure()    


    if 1: #Check ZZ -- SSB for lower qubit with ZZ for lower qubit in g vs e
        spec1 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, np.linspace(-4e6, 3e6, 201), proj_func='phase', seq=seq_cool)
        spec1.measure()
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit_info.rotate(np.pi,0)])
        spec1 = ssbspec.SSBSpec(qubit2_info, np.linspace(-5e6, 4e6, 201), proj_func='phase', seq=seq, extra_info=qubit_info)
        spec1.measure()    








#    from scripts.fluxonium import ssbspec_gaussianfit_ZZon
#    if 0: #Check ZZ -- SSB for upper qubit with ZZ for lower qubit in g vs e
#        spec1 = ssbspec_gaussianfit_ZZon.SSBSpec_Gaussianfit(qubit_info, offset_info, np.linspace(-15e6, 15e6, 81), proj_func='phase', seq=seq_cool)
#        spec1.measure()
#        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi,0)])
#        spec1 = ssbspec_gaussianfit_ZZon.SSBSpec_Gaussianfit(qubit_info, offset_info, np.linspace(-15e6, 15e6, 81), proj_func='phase', seq=seq, extra_info=qubit2_info)
#        spec1.measure()    






    
    if 0: #Check population after cooling:
        ZZ.set_rf_on(False)
        spec2 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-5e6,5e6, 81), proj_func='phase', seq=seq_cool)
        spec2.measure()
        spec2 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, np.linspace(-5e6, 5e6, 81), proj_func='phase', seq=seq_cool)
        spec2.measure()   
        ZZ.set_rf_on(True)
    
    if 0: #Rabi checking pi amps for upper qubit from both input lines
        tr1 = rabi.Rabi(gate_info1, np.linspace(-0.2, 0.2, 61), selective=False,
                                       plot_seqs=False, generate=True, repeat_pulse=1,
                                       update=True, seq=seq_cool, postseq=None, proj_func='phase')
        data=tr1.measure()
        tr1 = rabi.Rabi(gate_info2, np.linspace(-0.5, 0.5, 61), selective=False,
                                       plot_seqs=False, generate=True, repeat_pulse=1,
                                       update=True, seq=seq_cool, postseq=None, proj_func='phase')
        data=tr1.measure()
#    
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
        t2 = T2measurement.T2Measurement(gate_info1, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                         proj_func='phase', seq=seq_cool)
        t2.measure()
        t2 = T2measurement.T2Measurement(gate_info2, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
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


if 0: #Rabi checking pi amp for cz gate with pre post rotations 
    alz.set_naverages(2000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi/2,0), gate_info1.rotate(np.pi/2,0)])
#                          sequencer.Combined([cx_info.rotate(np.pi, 0), cancel_info.rotate(np.pi, 0)])])
#                          sequencer.Combined([cx_info.rotate(np.pi, 0), cancel_info.rotate(np.pi, 0)])
    postseq =  sequencer.Combined([gate_info1.rotate(np.pi/2,0), gate_info2.rotate(np.pi/2,0)])
    tr1 = rabi.Rabi(ZZ_info, np.linspace(-0.3,0.3, 101), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=4, cancel_info=None,
                                   update=True, seq=seq, postseq=postseq, proj_func='phase',
                                   extra_info=gate_info2,
                                   )
    data=tr1.measure()    
#    bla
if 0: #Rabi checking pi amp for single qubit gate  
    alz.set_naverages(4000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    postseq =  gate_info1.rotate(np.pi,0)

    tr1 = rabi.Rabi(gate_info1, np.linspace(-0.05,0.05, 101), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1, cancel_info=None,
                                   update=False, seq=seq_cool, postseq=postseq, proj_func='phase',
                                   extra_info=gate_info1,
                                   )
    data=tr1.measure()    
    bla

if 0: #CZ Rabi with echo
    alz.set_naverages(2500)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    tr1 = rabi_echo.Rabi(ZZ_info, gate_info1, gate_info2, np.linspace(-0.2,0.2, 201), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1, cancel_info=None,
                                   update=False, seq=seq, postseq=None, proj_func='phase',
                                   extra_info=gate_info2,
                                   )
    data=tr1.measure()    
    bla





if 1: # Time Rabi
    from scripts.single_qubit import timerabi
    alz.set_naverages(4000)
    cool = sequencer.Constant(int(10e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi,0)])   
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0)])    
    postseq =  gate_info1.rotate(np.pi,0)
#    postseq =  sequencer.Combined([gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])
    tr = timerabi.TimeRabi(qubit2_info2, np.linspace(0,1000, 81), amp=0.005, 
                           seq=seq_cool, postseq=None, proj_func='phase', plot_seqs=False, extra_info=qubit2_info) #extra_info=[gate_info1, gate_info2])
    data = tr.measure()
    bla



if 0: #2d time amp vs detuning 
    from scripts.fluxonium import Timerabi_det_2D
    cool = sequencer.Constant(int(5e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])   
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0)])    
#    postseq =  gate_info1.rotate(np.pi,0)
    timerabi_det = Timerabi_det_2D.Timerabi_det_2D(qubit2_info, np.linspace(1,250, 71), np.linspace(15e6,18e6,4), 
                                                   amp= 0.18,  
               sigma=4, seq=seq_cool, postseq=None, 
                control_pi=False, proj_func='phase', extra_info=[gate_info1, gate_info2])    
    data = timerabi_det.measure()
    bla



#if 0: #2d time amp for CZ tune up 
#    from scripts.fluxonium import Timerabi_amp_2D
#    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)])   
##    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0)])    
#    postseq =  gate_info1.rotate(np.pi,0)
#    timerabi_amp = Timerabi_amp_2D.Timerabi_amp_2D(qubit_info3, np.linspace(0,200,41), np.linspace(0.012,0.012,1),  
#               sigma=4, seq=seq_cool, postseq=postseq, 
#                control_pi=False, proj_func='phase', extra_info=[gate_info1, gate_info2])    
#    data = timerabi_amp.measure()
#    bla
#
#
#
#
#
#
#
#
#    
if 0: # Tune up for time vs relative amp
    rotation = 0.0
    X_proj = gate_info1.rotate(np.pi/2, np.pi/2+rotation)
    Y_proj = gate_info1.rotate(np.pi/2, rotation)
    
    cr_tune = CRtuning_time_amp.CRtuning_time_amp(gate_info1, gate_info2,  
                                                    np.linspace(1,400,21), rel_amps=np.linspace(4.5,4.8,21), 
                amp=0.079063, phase=0, rel_phase=-0.4635, sigma=4, seq=seq_cool, postseq=None, cancel_info=None,
                control_pi=False, proj_func='phase', extra_info=gate_info1)    
    data = cr_tune.measure()
    bla

#    
if 0: # Tune up for time vs relative amp
    rotation = 0.0
    X_proj = gate_info1.rotate(np.pi/2, np.pi/2+rotation)
    Y_proj = gate_info1.rotate(np.pi/2, rotation)
    cool = sequencer.Constant(int(5e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])   
    
    cr_tune = CRtuning_time_amp.CRtuning_time_amp(qubit_info, qubit_info2, qubit2_info2, 
                                                    np.linspace(1,50,31), rel_amps=np.linspace(0,1,11), 
                amp=0.1, phase=0, rel_phase=7.5, sigma=6, seq=seq_cool, postseq=None, cancel_info=None,
                control_pi=True, proj_func='phase', extra_info=qubit2_info)    
    data = cr_tune.measure()
    bla


    
if 0: # Tune up for time vs relative phase
    alz.set_naverages(2500)
#    rotation = 0.0
#    X_proj = gate_info1.rotate(np.pi/2, np.pi/2+rotation)
#    Y_proj = gate_info1.rotate(np.pi/2, rotation)
    cool = sequencer.Constant(int(5e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])   
    postseq = qubit2_info2.rotate(np.pi,0)
    cr_tune = CRtuning_time_phase.CRtuning_time_phase(qubit_info, qubit_info2, qubit2_info2,  
                                                    np.linspace(1,150,31), rel_phases=np.linspace(-4,-3,11), 
                amp=0.29, phase=0, rel_amp=0.0921, sigma=4, seq=seq_cool, postseq=postseq, cancel_info=None,
                control_pi=True, proj_func='phase',plot_seqs=False)    
    data = cr_tune.measure()
    bla


if 0: # Tune up for time vs detuning   
    
    from scripts.fluxonium import CRtuning_timevsdet
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
    cr_tune = CRtuning_timevsdet.CRtuning_timevsdet(gate_info1, gate_info2, 
                                                    np.linspace(0,100,31), np.linspace(-10e6, 10e6, 9), 
                amp=0.079591, phase=0, rel_amp=4.64, rel_phase=-0.4375, sigma=6, update=False, 
                seq=seq_cool, fix_phase=True, fix_period=None, control_pi=True, proj_func='phase')    
    
    data = cr_tune.measure()
    bla
    
if 0: # Tune up 1Q gates with Interleaved Time Rabi
    from scripts.fluxonium  import timerabi_interleaved_withqubitinfo
    alz.set_naverages(1500)
#    rotation = 0.6
#    X_proj = qubit2_info.rotate(np.pi/2, np.pi/2+rotation)
#    Y_proj = qubit2_info.rotate(np.pi/2, rotation)
#    rel_amp=0.550893
    rel_amp = 0.0921
    rel_phase = -1
#    rel_phase = -0.412
    for postseq in [qubit2_info2.rotate(np.pi,0)]:
        tr = timerabi_interleaved_withqubitinfo.TimeRabi_interleaved(
            qubit_info, qubit_info2, qubit2_info2, np.linspace(0, 500, 121), #Does not include Gaussian ramp time, sigma=4
            amp=0.29, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, sigma=4,
            update=False, seq=seq_cool, postseq=None, proj_func='phase', read_on_e=False)
        data = tr.measure()
    bla




if 1: 
    from scripts.fluxonium  import timerabi_interleaved_withqubitinfo
    alz.set_naverages(2000)
    
    cool = sequencer.Constant(int(5e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)]) 
    X_proj = qubit_info.rotate(np.pi/2, 0)#np.pi*0.30)
    Y_proj = qubit_info.rotate(np.pi/2, np.pi/2)

    rel_amp= 0.0921#-0.075317#-0.1259
    rel_phase = -1
#    for rel_amp in np.linspace(0.295, 0.298, 2):
    for i in range(1):
        for postseq in [qubit2_info2.rotate(np.pi,0)]:
            tr = timerabi_interleaved_withqubitinfo.TimeRabi_interleaved(
                qubit_info, qubit_info2, qubit2_info2, np.linspace(0, 500, 151), #Does not include Gaussian ramp time, sigma=4
                amp=0.29, phase=0, rel_amp=rel_amp, rel_phase=rel_phase, 
                update=False, seq=seq_cool, postseq=postseq, proj_func='phase')
            data = tr.measure()
    bla






        
if 0: # Tune up CR with Interleaved Time Rabi
    from scripts.fluxonium  import timerabi_interleaved_withqubitinfo
    alz.set_naverages(1000)
#    controlpi = gate_info2.rotate(np.pi, 0)
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
#    rotation = -0.08
    rotation = 0
    X_proj = gate_info1.rotate(np.pi/2, np.pi/2+rotation)
    Y_proj = gate_info1.rotate(np.pi/2, rotation)
    for rel_amp in [0.52]:
#    rel_amp= 4.457#5.03#4.4493
        for rel_phase in [7.5]: #1.011
#    rel_amp=4.4405
#    rel_phase=1.01
            
            for postseq in [None]:
                tr = timerabi_interleaved_withqubitinfo.TimeRabi_interleaved(
                            qubit_info, qubit_info2, qubit2_info, np.linspace(0, 500, 131), #Does not include Gaussian ramp time, sigma=4
                            amp=0.1, seq=seq_cool, postseq=None, proj_func='phase', plot_seqs=False, extra_info=None)
                data = tr.measure()
    bla
if 0: #Calibration of the CR-imprinted phase for control qubit in |g>
    from scripts.single_qubit import geophasecal
    alz.set_naverages(10000)

    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    X_proj = gate_info1.rotate(-np.pi/2, np.pi/2)
    Y_proj = gate_info1.rotate(np.pi/2, 0)

    for postseq in [gate_info2.rotate(np.pi,0)]:    
#        geoph = geophasecal.geophasecal(gate_info2, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
#                                            wait_reference = True, wait_time =(4+36) , repeat_pulse=1,
#                                            seq=seq, postseq=None, proj_func='phase', plot_seqs=False,
#                                            extra_info=gate_info2
#                                            )
#        data=geoph.measure() 
    
    
        geoph = geophasecal.geophasecal(gate_info2, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
                                            wait_reference = False, wait_time =(4+36) , repeat_pulse=1,
                                            seq=seq, postseq=None, proj_func='phase', plot_seqs=False,
                                            extra_info=gate_info2
                                            )
        data=geoph.measure() 
#    bla
    
        





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


#if 0: # Tune up for time vs detuning  #ebru - have not been troughly tested 
#    
#    from scripts.fluxonium import cphase_zztune
#    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
#    cr_tune = cphase_zztune.cphase_zztune(ZZ_info, offset_info, gate_info1, gate_info2,
#                                                    np.linspace(0,200,121), np.linspace(-285e6, -286e6,5), 
#                amp=0.15, phase=0, sigma=6, update=False, 
#                seq=seq_cool, fix_phase=True, fix_period=None,proj_func='phase')    
#    
#    data = cr_tune.measure()
#    bla
#

if 0: # 
    from scripts.fluxonium  import CZ_1Dseq  #this one has delays in between pi adnd pi/2's
    alz.set_naverages(2000)

    cz = CZ_1Dseq.TimeRabi_interleaved(
                            gate_info1, gate_info2, offset_info, np.linspace(0, 1000,51), #Does not include Gaussian ramp time, sigma=4
                            read_on_e=False,  
                            update=False, seq=seq_cool, postseq=None, proj_func='phase', plot_seqs=False, extra_info=None)
    data = cz.measure()
    
if 1: # for modified version
    from scripts.fluxonium  import CZ_1Dseq_modified
    alz.set_naverages(4000)
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    postseq = gate_info1.rotate(np.pi,0)
#    postseq =  sequencer.Combined([gate_info1.rotate(np.pi,0), gate_info2.rotate(np.pi,0)])
    cz = CZ_1Dseq_modified.TimeRabi_interleaved(
                                gate_info1, gate_info2, ZZ_info,  np.linspace(0, 100, 101), #Does not include Gaussian ramp time, sigma=4
                                amp=-0.118, phase=0, sigma=6, read_on_e=False,update=False, seq=seq, 
                                postseq=None, proj_func='phase', plot_seqs=False, extra_info=None)
    data = cz.measure()
#        ZZperiod.append(cz.fit_params['period'].value)
#        ZZperiod_err.append(cz.fit_params['period'].stderr)


if 0: #2d time amp for CZ tune up 
    from scripts.fluxonium import CZtuning_time_amp
    cr_tune = CZtuning_time_amp.CRtuning_time_amp(gate_info1, gate_info2, ZZ_info, 
                                                    np.linspace(1,60,11), amps=np.linspace(-0.2,-0.3,31), 
                phase=0,  sigma=8, seq=seq_cool, postseq=None, cancel_info=None,
                control_pi=False, proj_func='phase', extra_info=gate_info1)    
    data = cr_tune.measure()
    bla









#if 0: # 2d
    
#    from scripts.fluxonium import cz_2d
#    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
#    cr_tune = cz_2d.CRtuning_timevsdet(ZZ_info, gate_info1, gate_info2, 
#                                                    np.linspace(0,240,31), np.linspace(-200e6,-150e6, 9), 
#                amp=0.15, phase=0, sigma=6, update=False, 
#                seq=seq_cool, fix_phase=True, fix_period=None, proj_func='phase', plot_seqs=False)    
#    
#    data = cr_tune.measure()
#    bla




if 0: # Check histogramming
    from scripts.single_qubit import rabi, efrabi
    twpa = mclient.instruments['WF_xxx']
    ro = mclient.instruments['readout']
    alz = mclient.instruments['alazar']
    readoutbrick = mclient.instruments['RObrick']
    pump_freqs = np.linspace(7903.48e6, 7903.48e6, 1)
    pump_powers = np.linspace(-4.5, -4.5, 1)
    readout_powers = np.linspace(5, 5, 1)
    acq_len = [2240]
    alz.set_naverages(50000)
    SNRs_qubit1 = []
    SNRs_qubit2 = []
    for power in pump_powers:
        twpa.set_power(power)
        for freq in pump_freqs:
            twpa.set_frequency(freq)
            for acq in acq_len:
                alz.set_nsamples(acq)
                ro.set_pulse_len(acq - 200)
                tr = rabi.Rabi(gate_info1, [gate_info1.pi_amp,], seq= seq_cool, histogram=True, title='|eg>')
                tr.measure()
                ro.set_IQe(np.average(tr.shot_data[:]))
                tr = rabi.Rabi(gate_info1, [0.00001], seq= seq_cool, histogram=True, title='|gg>')
                tr.measure()
                ro.set_IQg(np.average(tr.shot_data[:]))
                tr1 = rabi.Rabi(gate_info1, [0.00001, gate_info1.pi_amp,], seq= seq_cool, histogram=True, proj_func='projection', title='|gg> and |eg>')
                tr1.measure()
                tr = rabi.Rabi(gate_info2, [gate_info2.pi_amp,], seq= seq_cool, histogram=True, title='|ge>')
                tr.measure()
                ro.set_IQe(np.average(tr.shot_data[:]))
#                tr2 = rabi.Rabi(gate_info2, [0.00001, gate_info2.pi_amp,], seq= seq_cool, histogram=True, proj_func='projection', title='|gg> and |ge>')
#                tr2.measure()
                gg_data = tr1.shot_data[::2]
                eg_data = tr1.shot_data[1::2]
                ge_data = tr.shot_data[:]
                print('gg phase: ', np.angle(np.average(gg_data), deg=True))
                print('eg phase: ', np.angle(np.average(eg_data), deg=True))
                print('ge phase: ', np.angle(np.average(ge_data), deg=True))
                SNR_qubit1 = np.abs(np.average(np.angle(gg_data, deg=True)) - np.average(np.angle(eg_data, deg=True)))/(np.std(np.angle(gg_data, deg=True))+np.std(np.angle(eg_data, deg=True)))
                print('SNR of qubit 1:', SNR_qubit1)
                SNR_qubit2 = np.abs(np.average(np.angle(gg_data, deg=True)) - np.average(np.angle(ge_data, deg=True)))/(np.std(np.angle(gg_data, deg=True))+np.std(np.angle(ge_data, deg=True)))
                print('SNR of qubit 2:', SNR_qubit2)
                SNRs_qubit1.append(SNR_qubit1)
                SNRs_qubit2.append(SNR_qubit2)
                plt.close('all')
    plt.plot(SNRs_qubit1)
    plt.plot(SNRs_qubit2)
        #
        
        #    tr = rabi.Rabi(gate_info1, [gate_info1.pi_amp,], seq=seq_cool, histogram=True, title='|eg>')
        #    tr.measure()
        #
        #    tr = rabi.Rabi(gate_info2, [gate_info2.pi_amp,], seq=seq_cool, histogram=True, title='|ge>')
        #    tr.measure()
        #
        #    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
        #    tr = rabi.Rabi(gate_info2, [gate_info2.pi_amp,], seq=seq, histogram=True, title='|ee>', extra_info = gate_info1)
        #    tr.measure()
        
        #    tr = efrabi.EFRabi(qubit_info, ef_info, [ef_info.pi_amp,], histogram=True, title='|f>')
        #    tr.measure()
    bla

if 0: #two-qubit histogramming
    from scripts.fluxonium import twoQ_histogram
    alz.set_naverages(50000)
    gg_phase = []
    eg_phase = []
    ge_phase = []
    twpa = mclient.instruments['WF_xxx']
    ro = mclient.instruments['readout']
    pump_freqs = np.linspace(  7904e6,  7905.5e6, 11)
    pump_powers = np.linspace(-2,-6,9)
    pulselens = np.linspace(2500,2500,1)
    for freq in pump_freqs:
        for power in pump_powers:
            for pulselen in pulselens:
                twpa.set_power(power)
                twpa.set_frequency(freq)
                ro.set_pulse_len(pulselen)
                tQh = twoQ_histogram.TwoQ_histogram(gate_info1, gate_info2, ['|gg>', '|eg>', '|ge>',], seq=seq_cool, histogram=True, proj_func='phase')
                tQh.measure()
                gg_data = tQh.shot_data[::3]
                eg_data = tQh.shot_data[1::3]
                ge_data = tQh.shot_data[2::3]
                gg_phase.append(np.angle(np.mean(gg_data), deg=True))
                eg_phase.append(np.angle(np.mean(eg_data), deg=True))
                ge_phase.append(np.angle(np.mean(ge_data), deg=True))
 
if 0: #single qubit tomography
    from scripts.single_qubit import Single_qubit_tomo
    alz.set_naverages(500000)
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    tomo = Single_qubit_tomo.Single_qubit_tomo(gate_info2, ZZ_info, CZ=True, repeat_pulse=1, 
                                               seq=seq, postseq=None, proj_func='phase', extra_info=ZZ_info)
    data = tomo.measure()
    alz.set_naverages(5000)
    
   

if 0: #two qubit tomography
    from scripts.fluxonium import twoqubit_state_tomo
    alz.set_naverages(100000)
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info2.rotate(np.pi,0)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150),
#                          gate_info1.rotate(np.pi/2,0), ZZ_info.rotate(np.pi,0),
#                          sequencer.Combined([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)]),
#                          ZZ_info.rotate(np.pi,0), gate_info1.rotate(np.pi/2,0)])
#    

    tomo = twoqubit_state_tomo.twoqubit_state_tomo(gate_info1, gate_info2, seq=seq, seq_cool=seq_cool, postseq=None, proj_func='phase', extra_info=ZZ_info)
    data = tomo.measure()
    alz.set_naverages(5000)
#I will integrate that part inside the analysis once it works fine    
    ys= tomo.get_ys()
#    A = np.array([[1, -1, -1,1],[1,-1,1,-1], [1,1,-1,-1] ,[1,1,1,1]])
    A = np.array([[1, 1, 1,1],[1,-1,1,-1], [1,1,-1,-1] ,[1,-1,-1,1]])

    B = np.array([ys[0], ys[1], ys[2], ys[3]])
    beta = np.linalg.solve(A,B)
    b0 = beta[0]
    b1 = beta[1]
    b2 = beta[2]
    b3 = beta[3]
    ys= ys - beta[0]

    IZ = (ys[4] + ys[5])/(2*b2)
    ZZ = (ys[5] + ys[6])/(-2*b3)
    ZI = (ys[4] + ys[6])/(2*b1)
    
#    YZ = (y[10]-y[7]+2*b2*IZ)/(-2*b3)
#
#    YI = (ys[10] + ys[7])/(2*b1)

    M_sub = np.array([[b1,b3],
                  [b1,-b3]])
    M_sub_vec =  np.array([ys[7] - b2*IZ, ys[10] +b2*IZ])
    M = np.linalg.solve(M_sub, M_sub_vec)
    YI = M[0]
    YZ = M[1]    



#    YZ = (y[7] - b1*YI - b2*IZ)/b3
    
    IX = (ys[17] + ys[18])/(-2*b2)

    ZX = (ys[18] + b1*ZI +b2 * IX)/b3
    
    IY = (ys[15]+ys[16])/(2*b2)
    
    ZY = (ys[15] - b1*ZI - b2*IY)/b3
    
    XI = (ys[11] + ys[14])/(-2*b1)
    
    XZ = (ys[14] + b1*XI +b2*IZ)/b3
    
    YY = (ys[8]- b1*YI - b2*IY)/b3
    
    YX = (ys[9] - b1*YI +b2*IX)/(-b3)
    
    XX = (ys[13] + b1*XI + b2*IX)/b3
    
    XY = (ys[12]+b1*XI -b2*IY)/(-b3)

#    YZ = (y[7] - b1*YI - b2*IZ)/b3

#    M_sub = np.array([[b1,b2,b3],
#                  [-1*b1,b2,-1*b3,],
#                  [b1,-1*b2,-1*b3]])
#    M_sub_vec =  np.array([ys[4], ys[5] , ys[6]])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    ZI = M[0]
#    IZ = M[1]
#    ZZ = M[2]
#    
#    M_sub = np.array([[b2,b3],
#                  [b2,-1*b3]])
#    M_sub_vec =  np.array([ys[15] - b1*ZI, ys[16] +b1*ZI])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    IY = M[0]
#    ZY = M[1]    
#    
#    
#    
#    
#    M_sub = np.array([[-b1,-b3],
#                  [-b1,b3]])
#    M_sub_vec =  np.array([ys[11] - b2*IZ, ys[14] +b2*IZ])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    XI = M[0]
#    XZ = M[1]    
#
#
#    M_sub = np.array([[b1,b3],
#                  [b1,-b3]])
#    M_sub_vec =  np.array([ys[7] - b2*IZ, ys[10] +b2*IZ])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    YI = M[0]
#    YZ = M[1]    

#    M_sub = np.array([[-b2,-b3],
#                  [-b2,b3]])
#    M_sub_vec =  np.array([ys[17] - b1*ZI, ys[18] +b1*ZI])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    IX = M[0]
#    ZX = M[1]    
#
#
#    
#    YY = (y[8] - b1*YI - b2* IY) / b3
#    M_sub = np.array([[b3]])
#    M_sub_vec =  np.array([y[8] - b1*YI - b2* IY])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    YY = M[0]
#
#    YX = (y[9] - (b1*YI - b2* IX)) / -b3
#    XY = (y[12] - (-b1*XI + b2* IY)) / -b3
#    XX = (y[13] - (-b1*XI - b2* IX)) / b3
    
    
    components = [ZI,IZ,ZX,ZY,ZZ,YI,IY,YX,YY,YZ,XI,IX,XX,XY,XZ]
    fig, ax = plt.subplots()
    plt.plot(components, linestyle="None", marker='o')    
    plt.bar([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14], components, width=0.2)    

    plt.xticks(np.arange(0,15,1))
    plt.legend()
    labels = [item.get_text() for item in ax.get_xticklabels()]

    labels[0]='ZI'
    labels[1] = 'IZ'
    labels[2] = 'ZX'
    labels[3] = 'ZY'
    labels[4] = 'ZZ'
    labels[5] = 'YI'
    labels[6] = 'IY'
    labels[7] = 'YX'
    labels[8] = 'YY'
    labels[9] = 'YZ'   
    labels[10] = 'XI'
    labels[11] = 'IX'
    labels[12] = 'XX'
    labels[13] = 'XY'
    labels[14] = 'XZ'
   
    ax.set_xticklabels(labels)
    plt.show()  
    






if 0: #two qubit process tomography
    from scripts.fluxonium import twoqubit_process_tomo
    alz.set_naverages(1000)
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150),
#                          gate_info1.rotate(np.pi/2,0), ZZ_info.rotate(np.pi,0),
#                          sequencer.Combined([gate_info2.rotate(np.pi,0), gate_info1.rotate(np.pi,0)]),
#                          ZZ_info.rotate(np.pi,0), gate_info1.rotate(np.pi/2,0)])
#    

    tomo = twoqubit_process_tomo.twoqubit_process_tomo(gate_info1, gate_info2, ZZ_info, seq=seq, seq_cool=seq_cool, postseq=None, proj_func='phase')
    data = tomo.measure()
    alz.set_naverages(5000)
#I will integrate that part inside the analysis once it works fine    
    ys= tomo.get_ys()
#    A = np.array([[1, -1, -1,1],[1,-1,1,-1], [1,1,-1,-1] ,[1,1,1,1]])
    A = np.array([[1, 1, 1,1],[1,-1,1,-1], [1,1,-1,-1] ,[1,-1,-1,1]])

    B = np.array([ys[0], ys[1], ys[2], ys[3]])
    beta = np.linalg.solve(A,B)
    b0 = beta[0]
    b1 = beta[1]
    b2 = beta[2]
    b3 = beta[3]
    ys= ys - beta[0]

    IZ = (ys[4] + ys[5])/(2*b2)
    ZZ = (ys[5] + ys[6])/(-2*b3)
    ZI = (ys[4] + ys[6])/(2*b1)
    
#    YZ = (y[10]-y[7]+2*b2*IZ)/(-2*b3)
#
#    YI = (ys[10] + ys[7])/(2*b1)

    M_sub = np.array([[b1,b3],
                  [b1,-b3]])
    M_sub_vec =  np.array([ys[7] - b2*IZ, ys[10] +b2*IZ])
    M = np.linalg.solve(M_sub, M_sub_vec)
    YI = M[0]
    YZ = M[1]    



#    YZ = (y[7] - b1*YI - b2*IZ)/b3
    
    IX = (ys[17] + ys[18])/(-2*b2)

    ZX = (ys[18] + b1*ZI +b2 * IX)/b3
    
    IY = (ys[15]+ys[16])/(2*b2)
    
    ZY = (ys[15] - b1*ZI - b2*IY)/b3
    
    XI = (ys[11] + ys[14])/(-2*b1)
    
    XZ = (ys[14] + b1*XI +b2*IZ)/b3
    
    YY = (ys[8]- b1*YI - b2*IY)/b3
    
    YX = (ys[9] - b1*YI +b2*IX)/(-b3)
    
    XX = (ys[13] + b1*XI + b2*IX)/b3
    
    XY = (ys[12]+b1*XI -b2*IY)/(-b3)

#    YZ = (y[7] - b1*YI - b2*IZ)/b3

#    M_sub = np.array([[b1,b2,b3],
#                  [-1*b1,b2,-1*b3,],
#                  [b1,-1*b2,-1*b3]])
#    M_sub_vec =  np.array([ys[4], ys[5] , ys[6]])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    ZI = M[0]
#    IZ = M[1]
#    ZZ = M[2]
#    
#    M_sub = np.array([[b2,b3],
#                  [b2,-1*b3]])
#    M_sub_vec =  np.array([ys[15] - b1*ZI, ys[16] +b1*ZI])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    IY = M[0]
#    ZY = M[1]    
#    
#    
#    
#    
#    M_sub = np.array([[-b1,-b3],
#                  [-b1,b3]])
#    M_sub_vec =  np.array([ys[11] - b2*IZ, ys[14] +b2*IZ])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    XI = M[0]
#    XZ = M[1]    
#
#
#    M_sub = np.array([[b1,b3],
#                  [b1,-b3]])
#    M_sub_vec =  np.array([ys[7] - b2*IZ, ys[10] +b2*IZ])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    YI = M[0]
#    YZ = M[1]    

#    M_sub = np.array([[-b2,-b3],
#                  [-b2,b3]])
#    M_sub_vec =  np.array([ys[17] - b1*ZI, ys[18] +b1*ZI])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    IX = M[0]
#    ZX = M[1]    
#
#
#    
#    YY = (y[8] - b1*YI - b2* IY) / b3
#    M_sub = np.array([[b3]])
#    M_sub_vec =  np.array([y[8] - b1*YI - b2* IY])
#    M = np.linalg.solve(M_sub, M_sub_vec)
#    YY = M[0]
#
#    YX = (y[9] - (b1*YI - b2* IX)) / -b3
#    XY = (y[12] - (-b1*XI + b2* IY)) / -b3
#    XX = (y[13] - (-b1*XI - b2* IX)) / b3
    
    
    components = [ZI,IZ,ZX,ZY,ZZ,YI,IY,YX,YY,YZ,XI,IX,XX,XY,XZ]
    fig, ax = plt.subplots()
    plt.plot(components, linestyle="None", marker='o')    
    plt.bar([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14], components, width=0.2)    

    plt.xticks(np.arange(0,15,1))
    plt.legend()
    labels = [item.get_text() for item in ax.get_xticklabels()]

    labels[0]='ZI'
    labels[1] = 'IZ'
    labels[2] = 'ZX'
    labels[3] = 'ZY'
    labels[4] = 'ZZ'
    labels[5] = 'YI'
    labels[6] = 'IY'
    labels[7] = 'YX'
    labels[8] = 'YY'
    labels[9] = 'YZ'   
    labels[10] = 'XI'
    labels[11] = 'IX'
    labels[12] = 'XX'
    labels[13] = 'XY'
    labels[14] = 'XZ'
   
    ax.set_xticklabels(labels)
    plt.show()  
    






























#
#if 0: #State population with SSB
#    ZZ.set_rf_on(False)
#    
#    #qubit 2
#    spec1 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, np.linspace(-4e6, 3e6, 81), proj_func='phase', seq=seq_cool)
#    spec1.measure()
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit_info.rotate(np.pi,0)])
#    spec1 = ssbspec.SSBSpec(qubit2_info, np.linspace(-4e6, 3e6, 181), proj_func='phase', seq=seq, extra_info=qubit_info)
#    spec1.measure()    
#   
# #fit initial conditions need to be changed here
##uncertainties need to be saved properly   
# 
#if  0:    #qubit 1
#    ZZ.set_rf_on(False)
#
#    spec1 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-4e6, 4e6, 81), proj_func='phase', seq=seq_cool)
#    spec1.measure()
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi,0)])
#    spec1 = ssbspec.SSBSpec(qubit_info, np.linspace(-4e6, 4e6, 181), proj_func='phase', seq=seq, extra_info=qubit2_info)
#    spec1.measure()    
