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
from pulseseq import sequencer, pulselib
#import matplotlib.pyplot as plt
import os
os.chdir(r'C:/qrlab/scripts')

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
cavity_infoA = mclient.get_qubit_info('cavityA')
#cavity_infoB = mclient.get_qubit_info('cavityB')


qubit_a1 = mclient.get_qubit_info('qubit_a1')
qubit_a2 = mclient.get_qubit_info('qubit_a2')
qubit_a3 = mclient.get_qubit_info('qubit_a3')
qubit_a4 = mclient.get_qubit_info('qubit_a4')
qubit_a5 = mclient.get_qubit_info('qubit_a5')
qubit_a6 = mclient.get_qubit_info('qubit_a6')


cA = cavity_infoA.rotate
ge = qubit_info.rotate
geqs = qubit_info.rotate_quasilective
ges = qubit_info.rotate_selective
ges_a1 = qubit_a1.rotate_selective
ges_a2 = qubit_a2.rotate_selective
ges_a3 = qubit_a3.rotate_selective


start_state = '0'
end_state = '04'
grape = sequencer.Join([sequencer.Trigger(250), 
                      sequencer.Combined([
                                          pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_' + start_state
                                                            + '_' + end_state + '_transmon_1000ns.csv', 
                                                            44, chan=qubit_info.sideband_channels[0]),
                                          pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_' + start_state
                                                            + '_' + end_state + '_cavity_1000ns.csv', 
                                                            144, chan=cavity_infoA.sideband_channels[0])
                                          ])
                    ])

grape2 = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_2_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_2_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0])
                                      ])
                ])
grape4 = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0])
                                      ])
                ])


grape6 = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_to_6_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_to_6_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_to_6_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_to_6_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])
                                      
grape_cat = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])
                                      
                                      
plus_cat = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])  

i_cat = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_cavity_1000ns.csv', 
                                                        -144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])  
                                     
re_data = np.real(np.loadtxt(r'C:\qrlab\pulseseq\CSVPulses\Gaussian_envelope_coherent_c_400ns.csv', dtype = complex))
im_data = np.imag(np.loadtxt(r'C:\qrlab\pulseseq\CSVPulses\Gaussian_envelope_coherent_c_400ns.csv', dtype = complex))
                                      
grape_displacement = sequencer.Join([sequencer.Trigger(250), 
                                     sequencer.Combined([pulselib.DataPulse(re_data, 125, chan=cavity_infoA.sideband_channels[0]),
                                                         pulselib.DataPulse(im_data, 125, chan=cavity_infoA.sideband_channels[1])
                                   ])])
                                 



if 1: # W function of OCT prepared states
    from scripts.single_cavity import WignerbyParity
    
    Wfun = WignerbyParity.WignerFunction(qubit_a2, ef_info, cavity_infoA, 
                                         xs = np.linspace(-2.2,2.2,13), ys = np.linspace(-2.2, 2.2, 13),
                                         t_ge=356, t_gf=0,
                                         seq=grape, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                         extra_info = [qubit_info]
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
                                             
    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
#                                        np.linspace(-21e6, -19e6, 31),
#                                        np.linspace(-11e6, -9e6, 31),
                                        np.linspace(-12e6, 0, 111),
                                       )), 
                           seq=grape6, plot_seqs=False, 
                           extra_info = [qubit_info, cavity_infoA]#, qubit_b0s, qubit_b2s, qubit_b4s, fwm_info, fwm_info_b2, fwm_info_b4]
                           )
    spec.measure_keysight()
    bla

if 0: # Can we try to make this happen?
    from single_cavity import cavT2
    detune = 30e3
    ct2 = cavT2.CavT2(qubit_info, cavity_infoA, .7, np.linspace(10e3, 200e3, 61), detune=detune, seq=None,
                       postseq=None, bgcor=False)
    ct2.measure_keysight()
    bla

if 0: # grape optimize
    from GRAPE import GRAPE_optimize

    op = GRAPE_optimize.GRAPE_optimize(qubit_info, qubit_a4, cavity_infoA, 
                                       np.linspace(35, 50, 11), np.linspace(115, 185, 13), 
                   plot_seqs=False, generate=True, seq=None, bgcor=False)
    op.measure_keysight()
    bla

if 0: # grape optimize
    from GRAPE import grape_timeshift

    ts = grape_timeshift.grape_timeshift(qubit_info, qubit_a4, cavity_infoA, np.arange(-10, 11),
                   plot_seqs=False, generate=True, seq=None)
    ts.measure_keysight()
    bla
            
            