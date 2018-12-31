import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import os
import time
import math

#alz = mclient.instruments['alazar']
#fg = mclient.instruments['funcgen']
os.chdir(r'C:/qrlab/scripts')
dig = mclient.instruments['dig']
#laserfg = mclient.instruments['laserfg']
#awg2 = mclient.instruments['AWG2']
#ag1 = mclient.instruments['ag1_RO']

#qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
qubit2_info = mclient.get_qubit_info('qubit2tone')

#cavity_infoR = mclient.get_qubit_info('cavity1R')
cavity_infoA = mclient.get_qubit_info('cavityAlice')
cavity_infoB = mclient.get_qubit_info('cavityBob')
#Qswitch_info1A = mclient.get_qubit_info('Qswitch1A')
#Qswitch_info1B = mclient.get_qubit_info('Qswitch1B')

#qubit_info2 = mclient.get_qubit_info('qDblCoax2')
#ef_info2 = mclient.get_qubit_info('eDblCoax2')
#cavity_info2A = mclient.get_qubit_info('cavity2A')
#cavity_info2B = mclient.get_qubit_info('cavity2B')

cA = cavity_infoA.rotate
cB = cavity_infoB.rotate
ge = qubit_info.rotate
ges= qubit_info.rotate_selective
geqs= qubit_info.rotate_quasilective
ef = ef_info.rotate
efs= ef_info.rotate_selective
efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))

geqs2 = qubit2_info.rotate_quasilective



'''
Qswitchseq = sequencer.Join([sequencer.Repeat(sequencer.Delay(100), 100),
            sequencer.Combined([
            sequencer.Repeat(sequencer.Constant(1000, 0.5, chan=Qswitch_info1A.sideband_channels[0]), 500),
            sequencer.Repeat(sequencer.Constant(1000, 0.5, chan=Qswitch_info1A.sideband_channels[1]), 500),
#            Repeat(Constant(250, 1, chan=5), 800),      # Qubit/Readout master switch
            ])])
'''
if 0: # Cavity disp calibration
    from single_cavity import cavdisp
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
    seq = sequencer.Trigger(250)
    disp = cavdisp.CavDisp(qubit_info, cavity_infoB, 2.5, 51, 0, seq=None,
                           delay=0, bgcor=False, update=False, generate=True,
#                           Qswitch_infoA=Qswitch_infoB, Qswitch_infoB=Qswitch_infoB,
#                           extra_info=[Qswitch_infoA, Qswitch_infoB,],
                          )
    disp.measure_keysight()
    bla

if 0: # Cavity T1
    from single_cavity import cavT1
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
    xs = np.concatenate((np.linspace(0e3, 50e3, 26), np.linspace(60e3, 1250e3, 55)))
    t1 = cavT1.CavT1(qubit_info, cavity_infoB, 0.9, xs,
                     proj_num=0, seq=None, postseq=None, bgcor=False, extra_info=[ef_info,])
    t1.measure_keysight()
    ys = t1.get_ys()
    bla

if 0:# Cavity T2
    from single_cavity import cavT2
    dataA = []
    
    detune = 50e3
    ct2b = cavT2.CavT2(qubit_info, cavity_infoA, .6, np.linspace(0e3, 300e3, 121), detune=detune, seq=None,
                       postseq=None, bgcor=False, extra_info=[qubit_info,])
    ct2b.measure_keysight()
    dataA.append(ct2b.get_ys())

#    for i in range(10):
#        t2 = cavT2.CavT2(qubit_info, cavity_infoA, 1.0, np.linspace(0, 1.0e6, 101), detune=10e3, seq=None,
#                         postseq=efpi, bgcor=False, extra_info=[ef_info,])
#        t2.measure()
    
if 0: #Cavity T2
    from single_cavity import cavT2
    dataB = []
    detune = 50e3
    ct2b = cavT2.CavT2(qubit_info, cavity_infoB, .7, np.linspace(0e3, 300e3, 121), detune=detune, seq=None,
                       postseq=None, bgcor=False, extra_info=[qubit_info,])
    ct2b.measure_keysight()
    dataB.append(ct2b.get_ys())

    bla


if 0: # Cavity spec
    from single_cavity import cavspectroscopy_keysight
    cav_freq = 3966.42e6
    freq_range = 2e6
    cspec = cavspectroscopy_keysight.CavSpectroscopy(mclient.instruments['Alicegen'], qubit_info, cavity_infoA, [np.pi], 
                                            np.linspace(cav_freq-freq_range, cav_freq+freq_range, 51))

    #This amplitude is NOT capped at 1 like on the qubit spec
    cspec.measure()
    bla




if 0: #SSB cavspec
    from single_cavity import ssbcavspec
    cspec = ssbcavspec.SSBCavSpec(qubit_info, cavity_infoA, np.linspace(-5e6, 5e6, 51),
#                                  postseq=efpi, extra_info=[ef_info,]
                                  )
    cspec.measure_keysight()
    bla
    
    
if 0: #cavity stark shift
    from single_cavity import ssbcavspec
    s = sequencer.Trigger(250)
    delay = 400e3
    s.append(sequencer.Combined([
        pulselib.Constant(int(delay-30e3), 1, chan='4m1'),
        pulselib.Constant(int(delay-30e3), .1, chan=self.fwm_info.sideband_channels[0]),
        pulselib.Constant(int(delay-30e3), .1, chan=self.fwm_info.sideband_channels[1]),
    ]))
    s.append(pulselib.Delay(30e3))
    cspec = ssbcavspec.SSBCavSpec(qubit_info, cavity_infoA, np.linspace(-5e6, 5e6, 71),
#                                  postseq=efpi, extra_info=[ef_info,]
                                  )
    cspec.measure_keysight()
    bla

if 0: # Measure cavity photon population
    from single_qubit import rabi
    tr = rabi.Rabi(qubit_info, np.linspace(-0.9, 0.9, 29), plot_seqs=False, update=False, seq=None, selective=1, singleshotbin=True)
    tr.measure_keysight()
#    period = tr.fit_params['period'].value
##    alz.set_naverages(4000)
#    tr = rabi.Rabi(qubit_info, np.linspace(-0.9, 0.9, 29), plot_seqs=False, update=False, seq=None, selective=1, singleshotbin=True, fix_period=period)
#    tr.measure_keysight()
    


if 0: #Sideband modulated number splitting:
    from single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate(1.8, 0)])
    spec = ssbspec.SSBSpec(qubit_info, #np.linspace(-30e6, 10e6, 21),
                           np.linspace(-15e6, 1e6, 101),#np.concatenate((np.linspace(-30.5e6, -26.5e6, 5),np.linspace(-13e6, -9e6, 8), np.linspace(-2.5e6, 1.5e6, 8))),
                           extra_info= cavity_infoA,
                           seq = seq,  plot_seqs=False)
    spec.measure_keysight()
    bla

if 0: #Multiple times Sideband modulated number splitting:
    from single_qubit import ssbspec
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(0, 0)])
    freq_array = np.concatenate((np.linspace(-31e6, -26e6, 30),np.linspace(-13e6, -9e6, 24), np.linspace(-2.5e6, 1.5e6, 24)))
#    freq_array = np.linspace(-1.7e6, 0.3e6, 51)
    spec = ssbspec.SSBSpec(qubit_info, freq_array,
                           extra_info= cavity_infoA,
                           seq = None,  plot_seqs=False)
    spec.measure_keysight()
    data_sum = spec.get_ys()
    for i in range (9):
#        seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(0, 0)])
        spec = ssbspec.SSBSpec(qubit_info, freq_array,
                               extra_info= cavity_infoA,
                               seq = None,  plot_seqs=False)
        spec.measure_keysight()
        data_sum = data_sum + spec.get_ys()
        data_avg = data_sum / (i+2)
    plt.figure()
    plt.plot(freq_array, data_avg)
    bla
 
if 0: #Alice spec with qubit pulse
    from single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = qubit_info.rotate(np.pi, 0)
    spec = ssbspec.SSBSpec(cavity_infoA, np.linspace(-15e6, 2e6, 51),
                           extra_info= qubit_info,
                           seq = seq,  postseq = postseq, plot_seqs=False)
    spec.measure_keysight()
    bla

if 0: #EF Sideband modulated number splitting:
    from single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(250), qubit_info.rotate(np.pi,0), cavity_infoB.rotate(1.2, 0)])
    postseq = qubit_info.rotate(np.pi,0)
#    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-14e6, 14e6, 121),
                           extra_info= [qubit_info, cavity_infoA],
                           seq =seq,  postseq = postseq, plot_seqs=False)
    spec.measure()
    bla

if 0: #mixer calibration:
    from single_qubit import mixer_calibration
    mixer_cal = mixer_calibration.Mixer_Calibration

    cal = mixer_cal('cavity1A', 4219.661700e6 , 'VA', 'AWG1', verbose=True,
                        base_amplitude = 4,
                        va_lo='ag2_JPC') # The frequency is the targeted lower sideband frequency, not the carrier

    cal.prep_instruments(reset_offsets=True, reset_ampskew=True)
    cal.tune_lo(mode='coarse')
    cal.tune_osb(mode=(0.15, 2000, 4, 1))
    cal.tune_lo(mode='fine') # useful if using 10 dB attenuation;
                            # LO leakage may creep up during osb tuning

    # this function will set the correct qubit_info sideband phase for use in experiments
    #    i.e. combines the AWG skew with the  7036.120e6current sideband phase offset
    cal.set_tuning_parameters(set_sideband_phase=True)
    cal.load_test_waveform()
    cal.print_tuning_parameters()
    bla

if 0: # test Q function
    from scripts.single_cavity import Qfunction
#    seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, 0)])
#    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=2.5, N=21, amaxx=None, Nx=None, amaxy=None, Ny=None,
#             seq=seq, delay=0, saveas=None, bgcor=False, extra_info=ef_info)
#    Qfun.measure()
    for dt in np.linspace(44e3, 47e3, 2):
#        seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, np.pi/2)])
#        seq.append(sequencer.Delay(dt))
        seq = sequencer.Join([sequencer.Trigger(250), cA(1.5, 0)])
        seq.append(sequencer.Delay(dt))
#        seq.append(cB(1.6, 0))
#        seq.append(ge(-np.pi, 0))
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoA, amax=1.8, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=0, saveas=None, bgcor=False, extra_info=ef_info)
        Qfun.measure_keysight()
    bla

if 1: # make a cat 
    from scripts.single_cavity import Qfunction
#    seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, 0)])
#    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=2.5, N=21, amaxx=None, Nx=None, amaxy=None, Ny=None,
#             seq=seq, delay=0, saveas=None, bgcor=False, extra_info=ef_info)
#    Qfun.measure()
    
#        seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, np.pi/2)])
#        seq.append(sequencer.Delay(dt))
    disp = 1.73
    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi/2, 0), 
                          cB(disp, 0), sequencer.Delay(300), cB(disp,0), 
                          sequencer.Combined([geqs2(np.pi, 0), geqs(np.pi, 0)]), 
                          cB(-disp+1.3,0)])
    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1.2, N=13, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, delay=0, saveas=None, bgcor=True, extra_info=ef_info)
    Qfun.measure_keysight()

    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi/2, 0), 
                          cB(disp, 0), sequencer.Delay(300), cB(disp,0), 
                          sequencer.Combined([geqs2(np.pi, 0), geqs(np.pi, 0)]), 
                          cB(-disp-1.3,0)])
    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1.2, N=13, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, delay=0, saveas=None, bgcor=True, extra_info=ef_info)
    Qfun.measure_keysight()
    
    
    bla

if 1: # Wigner function by displaced parity for cavity B
    from scripts.single_cavity import WignerbyParity
#    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
#                          geqs(pi,0), cB(-1.65, -pi*0.02)])    
#    seq = sequencer.Join([sequencer.Trigger(250), cB(.5, 0)])
    disp = 1.73
    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi/2, 0), 
                          cB(disp, 0), sequencer.Delay(300), cB(disp,0), 
                          sequencer.Combined([geqs2(np.pi, 0), geqs(np.pi, 0)]), 
                          cB(-disp,0)])
#    seq = sequencer.Join([sequencer.Trigger(250), 
#                          ge(np.pi, np.pi*0.0), 
#                          cB(disp, 0), sequencer.Delay(300), cB(disp, 0), 
##                          ge(np.pi, 0),
#                          sequencer.Combined([geqs2(np.pi, np.pi*0.0), geqs(np.pi, np.pi*0.0)]), 
##                          cB(-disp,0), cB(-disp, 0)
#                          ])
    
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB, t_ge=300, t_gf=0,
                                         amax=1.0, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                                         seq=seq, delay=5, saveas=None, bgcor=False)
    Wfun.measure_keysight()

if 0: # Wigner function by displaced parity for cavity A
    from scripts.single_cavity import WignerbyParity
#    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
#                          geqs(pi,0), cB(-1.65, -pi*0.02)])    
    seq = sequencer.Join([sequencer.Trigger(250), cA(0.5, 0)])
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoA, t_ge=125, t_gf=0,
                                         amax=1, N=13, amaxx=None, Nx=None, amaxy=None, Ny=None,
                                         seq=seq, delay=0, saveas=None, bgcor=False)
    Wfun.measure_keysight()
