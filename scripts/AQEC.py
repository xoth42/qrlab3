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
from pulseseq import sequencer#, pulselib
#import matplotlib.pyplot as plt
import os
os.chdir(r'C:/qrlab/scripts')

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
cavity_infoB = mclient.get_qubit_info('cavityB')


fwm_info = mclient.get_qubit_info('FWM_info')
fwm_info_b2 = mclient.get_qubit_info('FWM_info_b2')
fwm_info_b4 = mclient.get_qubit_info('FWM_info_b4')    
qubit_b0s = mclient.get_qubit_info('qubit_b0s')
qubit_b2s = mclient.get_qubit_info('qubit_b2s')
qubit_b4s = mclient.get_qubit_info('qubit_b4s')

qubit_b1 = mclient.get_qubit_info('qubit_b1')
qubit_b2 = mclient.get_qubit_info('qubit_b2')
qubit_b3 = mclient.get_qubit_info('qubit_b3')
qubit_b4 = mclient.get_qubit_info('qubit_b4')

c = cavity_infoB.rotate
ge = qubit_info.rotate
geqs = qubit_info.rotate_quasilective
ges = qubit_info.rotate_selective
ges_b1 = qubit_b1.rotate_selective


if 0: # poly ssbspec to find stark shift
    from FWM import poly_fwm_ssbspec
#    fwm_infos = [fwm_info, fwm_info_b2, fwm_info_b4]
#    fwm_amps = [x * .175 for x in [1., 1./np.sqrt(3), 1./np.sqrt(5)]]
    fwm_infos = [fwm_info]
    fwm_amps = [.175]
#    fwm_amps = [x * .0001 for x in [1., 1./np.sqrt(3), 1./np.sqrt(5)]]
    freqs = np.linspace(-1e6, 3e6, 71)
    delay_times=[50e3]
    ge_amps = [1.5e-3]
    for delay_t in delay_times:
        for ge_amp in ge_amps:
            ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_info, fwm_infos, 
                                                    freqs, delay_t, ge_amp, fwm_amps, 
                                                    plot_seqs=False)
            ssb.measure_keysight()
    bla


if 0: # SSB w/ e-o dissipation on coherence state
    from single_qubit import ssbspec
    dt = 50e3
    seq = sequencer.Join([sequencer.Trigger(250),
#                          c(0.561,0),
#                          ges(np.pi, 0), ges(np.pi, np.pi/2),
#                          c(-0.24,0)
#                          c(2.6, 0),
                          c(1.55,np.pi/2), 
                          sequencer.Combined([ges(2*np.pi, 0), ges_b1(2*np.pi, 0)]), 
                          c(-.44, np.pi/2),
#                          sequencer.Combined([sequencer.Constant(int(dt), 1.15e-3, chan=qubit_b0s.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), 1.15e-3, chan=qubit_b2s.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), 1.15e-3, chan=qubit_b4s.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), .30, chan=fwm_info.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), .30/np.sqrt(3), chan=fwm_info_b2.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), .30/np.sqrt(5), chan=fwm_info_b4.sideband_channels[0])
#                                              ]),
#                          sequencer.Delay(1e3)
                          ])
    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                        np.linspace(-15e6, -5e6, 121),

                                       )), 
                           seq=seq, plot_seqs=False, extra_info = [cavity_infoB, #qubit_b1,
#                                                                   qubit_b0s, qubit_b2s, qubit_b4s, fwm_info, fwm_info_b2, fwm_info_b4
                                                                   ])
    spec.measure_keysight()
    bla
    
if 0: # Q function w/ e-o dissipation on coherence state
    from scripts.single_cavity import Qfunction
    seq = sequencer.Join([sequencer.Trigger(250), 
                          c(1.5, 0),
                          sequencer.Combined([sequencer.Constant(int(25e3), 1e-3, chan=qubit_b0s.sideband_channels[0]),
                                              sequencer.Constant(int(25e3), 1e-3, chan=qubit_b2s.sideband_channels[0]),
                                              sequencer.Constant(int(25e3), 1e-3, chan=qubit_b4s.sideband_channels[0]),
                                              sequencer.Constant(int(25e3), .49, chan=fwm_info.sideband_channels[0]),
                                              sequencer.Constant(int(25e3), .49/np.sqrt(3), chan=fwm_info_b2.sideband_channels[0]),
                                              sequencer.Constant(int(25e3), .49/np.sqrt(5), chan=fwm_info_b4.sideband_channels[0])
                            ]),
                          sequencer.Delay(1e3)
                          ])
    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=2.1, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, postseq=None, delay=5, bgcor=True, 
                 extra_info = [qubit_b0s, fwm_info, qubit_b2s, qubit_b4s, fwm_info_b2, fwm_info_b4]
                 )
    Qfun.measure_keysight()
    bla

if 0: # W function w/ e-o dissipation on coherence state
    from scripts.single_cavity import WignerbyParity
    for dt in [85e3, 170e3, 255e3, 340e3]:
        seq = sequencer.Join([sequencer.Trigger(500), 
                              c(1.6, 0),
                              sequencer.Combined([sequencer.Constant(int(dt), 2e-3, chan=qubit_b0s.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), 2e-3/np.sqrt(3), chan=qubit_b2s.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), 2e-3/np.sqrt(5), chan=qubit_b4s.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), .49, chan=fwm_info.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), .49/np.sqrt(3), chan=fwm_info_b2.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), .49/np.sqrt(5), chan=fwm_info_b4.sideband_channels[0])
                                ]),
                              sequencer.Delay(1e3)
                              ])    
        Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB, 
                                             xs = np.linspace(-1.2,1.2,9), ys = np.linspace(-2.1,2.1,15),
                                             t_ge=320, t_gf=0,
                                             seq=seq, delay=5, bgcor=True, zmax=100, zmin=20, 
                                             extra_info = [qubit_b0s, fwm_info, qubit_b2s, qubit_b4s, fwm_info_b2, fwm_info_b4]
                                             )
        Wfun.measure_keysight()
    bla

if 1: # Vlastakis cat Wigner
    from scripts.single_cavity import WignerbyParity    
    for dt in [84e3, 86e3, 168e3, 172e3]:
        seq = sequencer.Join([sequencer.Trigger(500), c(1.7,0), ge(np.pi/2, 0), sequencer.Delay(320), c(1.7, 0),
                              geqs(np.pi, 1.1), c(-1.7, 0.05*np.pi/2),
                              sequencer.Combined([sequencer.Constant(int(dt), 1.5e-3, chan=qubit_b0s.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), 0.85e-3, chan=qubit_b2s.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), 0.7e-3, chan=qubit_b4s.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), .108, chan=fwm_info.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), .108/np.sqrt(3), chan=fwm_info_b2.sideband_channels[0]),
                                                  sequencer.Constant(int(dt), .108/np.sqrt(5), chan=fwm_info_b4.sideband_channels[0])
                                ]),
                              sequencer.Delay(1e3)
                              ])
        for x_start in [-2.3, -1.1, 0.1, 1.1]:
            Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB, 
#                                             xs = np.linspace(-2.1,2.1,15), ys = np.linspace(-1.5,1.5,11),
                                             xs = np.linspace(x_start,x_start+1.0, 6), ys = np.linspace(-2.2,2.2,23),
#                                             xs = np.linspace(-0.8,0.8,11), ys = np.linspace(-0.8,0.8,11),
                                             t_ge=320, t_gf=0,
                                             seq=seq, delay=5, bgcor=True, zmax=75, zmin=20, 
                                             extra_info = [qubit_b0s, fwm_info, qubit_b2s, qubit_b4s, fwm_info_b2, fwm_info_b4]
                                             )
            Wfun.measure_keysight()
    bla



if 0: # Vlastakis cat SSB
    from single_qubit import ssbspec
    dt = 50e3
    
    seq = sequencer.Join([sequencer.Trigger(500), c(1.4,0), ge(np.pi/2, 0), sequencer.Delay(320), c(1.4, 0),  # this was written for c(1.7,0)
                          geqs(np.pi, 1.1), c(-1.4, 0.05*np.pi/2),
#                          sequencer.Combined([sequencer.Constant(int(dt), 1.5e-3, chan=qubit_b0s.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), 0.85e-3, chan=qubit_b2s.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), 0.70e-3, chan=qubit_b4s.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), .108, chan=fwm_info.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), .108/np.sqrt(3), chan=fwm_info_b2.sideband_channels[0]),
#                                              sequencer.Constant(int(dt), .108/np.sqrt(5), chan=fwm_info_b4.sideband_channels[0])
#                                              ]),
                        sequencer.Delay(500)
                        ])
    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                        np.linspace(-10e6, 1e6, 101),
                                       )), 
                           seq=seq, plot_seqs=False, 
                           extra_info = [cavity_infoB,
#                                         qubit_b0s, qubit_b2s, qubit_b4s, fwm_info, fwm_info_b2, fwm_info_b4
                           ])
    spec.measure_keysight()
    bla

if 0: # Kerr revival test
    from scripts.single_cavity import Qfunction
    for dt in [160e3, 180e3, 200e3, 220e3, 240e3]:
        seq = sequencer.Join([sequencer.Trigger(250), 
                              c(1.5, 0),
                              sequencer.Delay(dt)
                              ])    
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=2.1, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, postseq=None, delay=5, bgcor=False, 
                     )
        Qfun.measure_keysight()
        Wfun.measure_keysight()


#for df in np.linspace(-50e3, 150e3, 11):
if 0: # time domain
    from FWM import poly_time_domain
#    fwm_info_b2.deltaf = -66.9e6+df
#    qubit_b2s.deltaf = -104.1e6-df
    fwm_infos = [fwm_info, fwm_info_b2, fwm_info_b4]
    fwm_amps = [x * .108 for x in [1., 1./np.sqrt(3), 1./np.sqrt(5)]]
    ge_infos = [qubit_b0s, qubit_b2s, qubit_b4s]
    ge_amps = [x * 1.0e-3 for x in [1.5, 0.85, 0.7]]
    qubit_list = [qubit_info, qubit_b1, qubit_b2, qubit_b3]#, qubit_b4]
    
    delays = np.linspace(0e3, 40e3, 21)
    seq = sequencer.Join([sequencer.Trigger(250), 
#                          c(1.4,0), ge(np.pi/2, 0), sequencer.Delay(320), c(1.4, 0),
#                          geqs(np.pi, 1.1+np.pi), c(-1.4, 0.05*np.pi/2), #This was written for c(1.7)
                          c(1.55,0), 
                          sequencer.Combined([ges(2*np.pi, 0), ges_b1(2*np.pi, 0)]), 
                          c(-.44, 0),
                          ]) # this makes a 2 fock state
    td = poly_time_domain.poly_time_domain(fwm_infos+ge_infos, fwm_amps+ge_amps, qubit_list, delays,
                                       plot_seqs=False, bgcor=True, seq=seq, 
                                       extra_info = cavity_infoB
                                       )
    td.measure_keysight()
bla
    
    
if 1: # SNAP 0 to 2 gate
    from single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(250), 
                          c(1.55,0), 
                          sequencer.Combined([ges(2*np.pi, 0), ges_b1(2*np.pi, 0)]), 
                          c(-.44, 0),
                          ])
#    seq = sequencer.Join([sequencer.Trigger(250), 
#                          c(1.14,0), 
#                          ges(2*np.pi, 0),
#                          c(-.56, 0)])
    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                        np.linspace(-10e6, 1e6, 81),
                                       )), 
                           seq=seq, plot_seqs=False, 
                           extra_info = [cavity_infoB, qubit_b1]#, qubit_b0s, qubit_b2s, qubit_b4s, fwm_info, fwm_info_b2, fwm_info_b4]
                           )
    spec.measure_keysight()
    bla
    
if 0: # Calibrate selective pi pulse at different photon numbers
    from single_qubit import rabi

    seq = sequencer.Join([sequencer.Trigger(250), 
                          c(1.14,0), 
                          ges(2*np.pi, 0),
                          c(-.56, 0)])
    tr = rabi.Rabi(qubit_b1, 
#                   np.linspace(-0.7, 0.7, 51), selective=False,    
                  np.linspace(-0.025, 0.025, 51), selective=True,
#                   np.linspace(-0.1, 0.1, 41), selective=.5,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, seq=seq,
                   extra_info=[cavity_infoB, qubit_info])
    tr.measure_keysight()
    bla