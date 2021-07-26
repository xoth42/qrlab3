"""
Tuneup file for AQEC. Hopefully running this file will gather all the relevant info and retune stuff.

"""

import mclient
import importlib
importlib.reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib, OCTlib
#import matplotlib.pyplot as plt
import os
os.chdir(r'C:/qrlab/scripts')

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
cavity_infoA = mclient.get_qubit_info('cavityA')
cavity_infoAs = mclient.get_qubit_info('cavityAs')
dig = mclient.instruments['dig']
fwm_info = mclient.get_qubit_info('FWM_info')

qubit_a1 = mclient.get_qubit_info('qubit_a1')
qubit_a2 = mclient.get_qubit_info('qubit_a2')
qubit_a3 = mclient.get_qubit_info('qubit_a3')
qubit_a4 = mclient.get_qubit_info('qubit_a4')
qubit_a5 = mclient.get_qubit_info('qubit_a5')
qubit_a6 = mclient.get_qubit_info('qubit_a6')
qubit_a7 = mclient.get_qubit_info('qubit_a7')


ge = qubit_info.rotate
cA = cavity_infoA.rotate
ge = qubit_info.rotate
geqs = qubit_info.rotate_quasilective
ges = qubit_info.rotate_selective
ges_a1 = qubit_a1.rotate_selective
ges_a2 = qubit_a2.rotate_selective
ges_a3 = qubit_a3.rotate_selective


chi2 = 2.655e6

cav_amp = 115
qt_amp = 44
time_shift = 11      
lib = OCTlib.octlib(qt_amp, cav_amp, time_shift, qubit_info, cavity_infoA, decode_info=cavity_infoAs)


ss = 2.5546e6   #AQEC with ~7us rates
fwm_comb = OCTlib.comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.15, 0.9, 0.55, 0.6]], vary = [1]*4, stark_shift = ss)
ge_comb = OCTlib.comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-.85, 1.25, 1.05, 1.35]], vary = [-1]*4, stark_shift = -ss)


if 0: # T1
    from .single_qubit import T1measurement
    t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 19e3, 20), np.linspace(20e3, 160e3, 20))), 
                                     double_exp=False, generate=True, plot_seqs=False, seq=None)
    t1_data = t1.measure_keysight()

if 0: # T2
    from .single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0e3, 30e3, 101), detune=0.3e6, 
#    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 3.9e3, 81), detune=2e6, 
                                     double_freq=False, generate=True, seq=None,
                                     plot_seqs=False)
    t2_data = t2.measure_keysight()


if 0: # Cavity T2
    from .single_cavity import cavT2
    detune = 10e3
    ct2 = cavT2.CavT2(qubit_info, cavity_infoA, .7, np.linspace(0, 400e3, 41), detune=detune, seq=None,
#    ct2 = cavT2.CavT2(qubit_info, cavity_infoA, .7, np.linspace(0, 3.99e3, 51), detune=2e6, seq=None,
                       postseq=None, bgcor=False)
    ct2_data = ct2.measure_keysight()


if 0: # Measure AQEC Rates
    from .FWM import poly_time_domain
    delays = np.concatenate((np.linspace(0e3, 20e3, 21), np.linspace(21e3, 70e3, 15)))
    
    td0 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a1], delays, bgcor=True, seq=None, 
                                       extra_info = [qubit_info, cavity_infoA], skip_points = 4)
    rate_01 = td0.measure_keysight()
    
    seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('2')])
    td2 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a3], delays, bgcor=True, seq=seq, 
                                       extra_info = [qubit_info, cavity_infoA], skip_points = 4)
    rate_23 = td2.measure_keysight()
    
    dig.set_trigger_period(3000)
    seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state_two_file('4')])
    td4 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a5,], delays, bgcor=True, seq=seq, 
                                       extra_info = [qubit_info, cavity_infoA], skip_points = 4)
    rate_45 = td4.measure_keysight()
    
    seq = sequencer.Join([sequencer.Trigger(200), lib.fock_state('6')])
    td6 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a7,], delays, bgcor=True, seq=seq,
                                       extra_info = [qubit_info, cavity_infoA], skip_points = 4)
    rate_67 = td6.measure_keysight()

if 0:
    print(('qubit t1 ', t1_data))
    print(('qubit t2 ', t2_data))
    print(('cavity t2 ', ct2_data))
    print(('rates ', rate_01['tau'].value, rate_23['tau'].value, rate_45['tau'].value, rate_67['tau'].value))


if 1: # bloch characterization
#    dig.set_trigger_period(4000)
#    dig.set_naverages(1000)
    from .AQEC import time_bloch

#    times = np.arange(0e3, 290e3, 70e3)
    times = np.linspace(0, 400e3, 7)
    bloch = [
             [ge(np.pi, 0)],
             [ge(np.pi/2, np.pi/2)],
             [ge(-np.pi/2, np.pi/2)],
             [ge(-np.pi/2, 0)],
             [ge(np.pi/2, 0)],
             ]
    bloch_targets = [
                     [0, 0, 1],
                     [-1, 0, 0],
                     [1, 0, 0],
                     [0, -1, 0],
                     [0, 1, 0]
                     ]
    for i, state_prep in enumerate(bloch):
        target = bloch_targets[i]
        seq = [sequencer.Trigger(200)] + state_prep + [lib.fock01_encode()]

        tb = time_bloch.time_bloch(qubit_info, times, seq = seq,
                                   target_state = target,
                                   extra_info = [cavity_infoA, cavity_infoAs],
                                   postseq = lib.fock01_encode(),
                                   background_fidelity = .5,
                                   kerr_correction = None,
#                                   plot_seqs = True,
#                                   comb_list = [fwm_comb, ge_comb],
                                   measure_ge = True
                                   )
        tb.measure_keysight()
            


if 0: # GRAPE ge test
    from .GRAPE import GRAPE_Rabi

    tr = GRAPE_Rabi.GRAPE_Rabi(qubit_info, np.linspace(-1e2, 1e2, 51), 
                   r'C:\qrlab-3\pulseseq\CSVPulses\gaussian_envelope_t_g_to_e_400ns.csv',
#                  np.linspace(-0.016, 0.016, 51), selective=True,
#                   np.linspace(-0.1, 0.1, 41), selective=.5,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, seq=None)
    tr.measure_keysight()
    bla
    
if 0: # GRAPE displacement test
    from .GRAPE import GRAPE_CavDisp
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
    seq = sequencer.Trigger(250)

    disp = GRAPE_CavDisp.GRAPE_CavDisp(qubit_info, cavity_infoA, 300, 41, 0,
                                       r'C:\qrlab-3\pulseseq\CSVPulses\Gaussian_envelope_coherent_c_400ns.csv', 
                                       seq=None, delay=0, bgcor=True, update=False, generate=True, plot_seqs = False,
#                           Qswitch_infoA=Qswitch_infoB, Qswitch_infoB=Qswitch_infoB,
#                           extra_info=[Qswitch_infoA, Qswitch_infoB,],
                          )
    disp.measure_keysight()
    bla




if 0: # grape optimize
    from .GRAPE import GRAPE_optimize

    logic_1 = sequencer.Join([sequencer.Trigger(200), ge(np.pi, 0)]) # Fock 3+7
    logic_plus = sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, np.pi/2)]) #vertical cat
    logic_minus = sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, np.pi*3/2)]) #horizontal cat
    logic_plus_i = sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, np.pi)])
    logic_minus_i = sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, 0)])

#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi/2, np.pi*3/2)])
    for seq in [logic_minus, logic_plus_i, logic_minus_i]:
        op = GRAPE_optimize.GRAPE_optimize(qubit_info, qubit_a2, cavity_infoA, 
                                           np.linspace(41, 48, 8), np.linspace(92, 110, 10), 
                                           plot_seqs=False, generate=True, seq=seq, bgcor=False)
        op.measure_keysight()
    bla

if 0: # grape optimize time shift
    from .GRAPE import grape_timeshift

    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi/2, np.pi/2)])
    ts = grape_timeshift.grape_timeshift(qubit_info, qubit_a2, cavity_infoA, np.arange(1, 28),
                   plot_seqs=False, generate=True, seq=None)
    ts.measure_keysight()
    bla
    
if 0: # encode-decode optimize
    from .GRAPE import encode_decode
    cavityAs = mclient.instruments['cavityAs']

    seq = sequencer.Join([sequencer.Trigger(250)])

    ed = encode_decode.encode_decode(qubit_info, cavity_infoA, cavity_infoAs, 'cav_amp', 
                                     np.arange(110, 120), '-z',
                                     q_amp=44, cav_amp=102, time_shift=11, g_value=160, e_value=20,
                                     seq=seq, postseq=None)
    ed.measure_keysight()
    bla
    