# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 14:03:37 2019

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 14:53:09 2018

@author: wanglab111
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib, OCTlib
#import matplotlib.pyplot as plt
import os
os.chdir(r'C:/qrlab/scripts')

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
cavity_infoA = mclient.get_qubit_info('cavityA')
#cavity_infoAs = mclient.get_qubit_info('cavityAs')


qubit_a1 = mclient.get_qubit_info('qubit_a1')
qubit_a2 = mclient.get_qubit_info('qubit_a2')
qubit_a3 = mclient.get_qubit_info('qubit_a3')
qubit_a4 = mclient.get_qubit_info('qubit_a4')
qubit_a5 = mclient.get_qubit_info('qubit_a5')
qubit_a6 = mclient.get_qubit_info('qubit_a6')

ge = qubit_info.rotate
cA = cavity_infoA.rotate
ge = qubit_info.rotate
geqs = qubit_info.rotate_quasilective
ges = qubit_info.rotate_selective
ges_a1 = qubit_a1.rotate_selective
ges_a2 = qubit_a2.rotate_selective
ges_a3 = qubit_a3.rotate_selective


cav_amp = 112
qt_amp = 43
time_shift = 11    
lib = OCTlib.octlib(qt_amp, cav_amp, time_shift, qubit_info, cavity_infoA)


if 0: # W function of OCT prepared states
    from scripts.single_cavity import WignerbyParity
#    for state in ['-z']:#, '-x', '+x', '-y']:
#        seq = sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])
#        Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoAs, 
#                                             xs = np.linspace(-2,2,9), ys = np.linspace(-2,2,9),
#                                             t_ge=356, t_gf=0,
#                                             seq=seq, delay=5, bgcor=True, zmax=125, zmin=-125, 
#                                             extra_info = [qubit_info]
#                                             )
#        Wfun.measure_keysight()
    seq = sequencer.Join([sequencer.Trigger(200), lib.alpha2()])

    Wfun = WignerbyParity.WignerFunction(qubit_a4, ef_info, cavity_infoA, 
                                         xs = np.linspace(-2,2,15), ys = np.linspace(-2,2,15),
                                         t_ge=356, t_gf=0,
                                         seq=seq, delay=5, bgcor=True, zmax=125, zmin=-125,
                                         extra_info = [qubit_info, cavity_infoA],
                                         rotation = 0, #The total pulse time until cavdisp is 200ns + 20ns + 1.013us + 50ns = 1.283us
#                                         plot_seqs = True
                                         )
    Wfun.measure_keysight()
    bla

if 0: # GRAPE ge test
    from GRAPE import GRAPE_Rabi

    tr = GRAPE_Rabi.GRAPE_Rabi(qubit_info, np.linspace(-1e2, 1e2, 51), 
                   r'C:\qrlab\pulseseq\CSVPulses\gaussian_envelope_t_g_to_e_400ns.csv',
#                  np.linspace(-0.016, 0.016, 51), selective=True,
#                   np.linspace(-0.1, 0.1, 41), selective=.5,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, seq=None)
    tr.measure_keysight()
    bla
    
if 0: # GRAPE displacement test
    from GRAPE import GRAPE_CavDisp
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
    seq = sequencer.Trigger(250)

    disp = GRAPE_CavDisp.GRAPE_CavDisp(qubit_info, cavity_infoA, 300, 41, 0,
                                       r'C:\qrlab\pulseseq\CSVPulses\Gaussian_envelope_coherent_c_400ns.csv', 
                                       seq=None, delay=0, bgcor=True, update=False, generate=True, plot_seqs = False,
#                           Qswitch_infoA=Qswitch_infoB, Qswitch_infoB=Qswitch_infoB,
#                           extra_info=[Qswitch_infoA, Qswitch_infoB,],
                          )
    disp.measure_keysight()
    bla
        
    
if 0: # GRAPE test number splitting    
    from single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(200), lib.mod4_prep('-z')])

    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
#                                        np.linspace(-21e6, -19e6, 31),
#                                        np.linspace(-11e6, -9e6, 31),
                                        np.linspace(-11e6, .5e6, 111),
                                       )), 
                           seq=seq, plot_seqs=False, 
                           extra_info = [qubit_info, cavity_infoA]#, qubit_b0s, qubit_b2s, qubit_b4s, fwm_info, fwm_info_b2, fwm_info_b4]
                           )
    spec.measure_keysight()
    bla

if 0: # grape optimize
    from GRAPE import GRAPE_optimize

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
    from GRAPE import grape_timeshift

    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi/2, np.pi/2)])
    ts = grape_timeshift.grape_timeshift(qubit_info, qubit_a2, cavity_infoA, np.arange(1, 28),
                   plot_seqs=False, generate=True, seq=None)
    ts.measure_keysight()
    bla
    
if 1: # encode-decode optimize
    from GRAPE import encode_decode
    dig.set_trigger_period(2500)
    dig.set_naverages(3000)
    for state in ['+z', '-z', '-x']:
        seq = sequencer.Join([sequencer.Trigger(250)])
    
#        ed = encode_decode.encode_decode(qubit_info, cavity_infoA, 'phase', 
#                                         np.arange(-0.9, 1.0, 0.1), state, 
#                                         q_amp=43.3, cav_amp=114.4, time_shift=11, g_value=145, e_value=21,
#                                         seq=seq, postseq=None, plot_seqs = False)
#        ed.measure_keysight()
#        
#        ed = encode_decode.encode_decode(qubit_info, cavity_infoA, 'q_amp',
#                                         np.arange(40.5, 46, 0.5), state, 
#                                         q_amp=43.3, cav_amp=114.4, time_shift=11, g_value=145, e_value=21,
#                                         seq=seq, postseq=None, plot_seqs = False)
#        ed.measure_keysight()    
        
        ed = encode_decode.encode_decode(qubit_info, cavity_infoA, 'cav_amp',
                                         np.arange(110, 121, 1), state, 
                                         q_amp=43.3, cav_amp=114.4, time_shift=11, g_value=145, e_value=21,
                                         seq=seq, postseq=None, plot_seqs = False)
        ed.measure_keysight()      
    bla
    
if 0: # Wigner line cut
    from scripts.AQEC import wigner_line_cut
    
    chi = []
    for qt_amp in np.linspace(46, 46, 1):
#        time_shift = 16
#        cav_amp = 97
#    
#        mod4_qt_I = sequencer.Join([pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_transmon_1000ns.csv', 
#                                                            qt_amp, chan=qubit_info.sideband_channels[0]),
#                                    sequencer.Constant(time_shift, 0, chan=qubit_info.sideband_channels[0])])
#        
#        mod4_qt_Q = sequencer.Join([pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_transmon_q_1000ns.csv', 
#                                                            qt_amp, chan=qubit_info.sideband_channels[1]),
#                                    sequencer.Constant(time_shift, 0, chan=qubit_info.sideband_channels[1])])
#        
#        mod4_cav_I = sequencer.Join([sequencer.Constant(time_shift, 0, chan=cavity_infoA.sideband_channels[0]),
#                                     pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_cavity_1000ns.csv', 
#                                                            cav_amp, chan=cavity_infoA.sideband_channels[0])])
#        
#        mod4_cav_Q = sequencer.Join([sequencer.Constant(time_shift, 0, chan=cavity_infoA.sideband_channels[1]),
#                                     pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_cavity_q_1000ns.csv', 
#                                                            cav_amp, chan=cavity_infoA.sideband_channels[1])])
#        
#        mod4_encode = sequencer.Combined([mod4_qt_I, mod4_qt_Q, mod4_cav_I, mod4_cav_Q])
#        
#        seq = [sequencer.Trigger(200), mod4_encode] #ge(np.pi/2, -np.pi/2), 
#        wp = wigner_line_cut.wigner_line_cut(qubit_a2, cavity_infoA, np.linspace(-1.5, 1.5, 41), 
#                                               y=0, rotation = 0, t_ge=356,
#                                               seq=logic_plus, delay=5, bgcor=True,
#                                               extra_info = [qubit_info, cavity_infoA],
#                                               plot_seqs = False,
#                                               fit = True
#                                               )
#        chi += [wp.measure_keysight()]
        seq = sequencer.Join([sequencer.Trigger(200), lib.mod4_prep(state)])
        wp = wigner_line_cut.wigner_line_cut(qubit_a2, cavity_infoA, np.linspace(-2.2, 2.2, 41), 
                                               y=0, rotation = np.pi/2, t_ge=356,
                                               seq=seq, delay=5, bgcor=True,
                                               extra_info = [qubit_info, cavity_infoA],
                                               plot_seqs = False,
                                               fit = True
                                               )
        chi += [wp.measure_keysight()]
    print chi


    bla
    
    
    
if 0: # bloch characterization
    from AQEC import time_bloch
    qubit_bloch = [sequencer.Trigger(200),
                   sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, 0)]),
                   sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, np.pi/2)]),
                   sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, np.pi)]),
                   sequencer.Join([sequencer.Trigger(200), ge(np.pi/2, np.pi*3/2)]),
                   sequencer.Join([sequencer.Trigger(200), ge(np.pi, 0)])]
    bloch_targets = [[0, 0, -1],
                     [1, 0, 0],
                     [0, 1, 0],
                     [-1, 0, 0],
                     [0, -1, 0],
                     [0, 0, 1]]
    
    seq = sequencer.Join([sequencer.Trigger(200),
#                          ge(np.pi/2, 0), 
                          mod4_encode
                          ])
    
    
#    for q_seq in :
    for target in [[0,0,-1]]:
        tb = time_bloch.time_bloch(qubit_info, np.linspace(0, 300e3, 50), 
                                   g_value=190, e_value=25, seq = seq,
                                   target_state = target,
                                   extra_info = [cavity_infoA, cavity_infoAs],
                                   postseq = mod4_decode,
                                   plot_seqs = False
                                   )
        tb.measure_keysight()
#                                       g_value = 175, e_value = 23,
#                                       extra_info = [cavity_infoA],
#                                       )