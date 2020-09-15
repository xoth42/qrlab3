import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
#import matplotlib.pyplot as plt
import os
os.chdir(r'C:/qrlab/scripts')


import matplotlib.pyplot as plt


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
#qubit2_info = mclient.get_qubit_info('qubit2tone')

#cavity_infoR = mclient.get_qubit_info('cavity1R')
cavity_infoA = mclient.get_qubit_info('cavityA')
#cavity_infoAs = mclient.get_qubit_info('cavityAs')
cavity_infoB = mclient.get_qubit_info('cavityB')
#cavity_infoR = mclient.get_qubit_info('cavityR')
#Qswitch_info1A = mclient.get_qubit_info('Qswitch1A')
#Qswitch_info1B = mclient.get_qubit_info('Qswitch1B')

#qubit_info2 = mclient.get_qubit_info('qDblCoax2')
#ef_info2 = mclient.get_qubit_info('eDblCoax2')
#cavity_info2A = mclient.get_qubit_info('cavity2A')
#cavity_info2B = mclient.get_qubit_info('cavity2B')

cA = cavity_infoA.rotate
cB = cavity_infoB.rotate
#cBqs = cavity_infoB.rotate_quasilective
ge = qubit_info.rotate
ges= qubit_info.rotate_selective
geqs= qubit_info.rotate_quasilective
#ef = ef_info.rotate
#efs= ef_info.rotate_selective
#efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))

#geqs2 = qubit2_info.rotate_quasilective

#fwm_info = mclient.get_qubit_info('FWM_info')


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

#for i in range(5):
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
#    dig.set_trigger_period(5000)
    disp = cavdisp.CavDisp(qubit_info, cavity_infoB, 2, 41, 0, seq=None,
                           delay=0, bgcor=True, update=True, generate=True,
                           plot_seqs = False
#                           Qswitch_infoA=Qswitch_infoB, Qswitch_infoB=Qswitch_infoB,
#                           extra_info=[Qswitch_infoA, Qswitch_infoB,],
                          )
    disp.measure_keysight()
    bla


if 0: # Cavity T1
    from single_cavity import cavT1
#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
#    xs = np.concatenate((np.linspace(0e3, 50e3, 26), np.linspace(60e3, 1250e3, 55)))

    t1 = cavT1.CavT1(qubit_info, cavity_infoB, 2, np.linspace(1e3, 2000e3, 51),
                     proj_num=0, seq=None, postseq=None, bgcor=True, force_a0 = True
#                     extra_info=[ef_info,]
                     )
    t1.measure_keysight()
#    ys = t1.get_ys()
    bla

if 0: # Cavity T2
    from single_cavity import cavT2
    detune = 15e3
    ct2 = cavT2.CavT2(qubit_info, cavity_infoB, .7, np.linspace(10e3, 400e3, 91), detune=detune, seq=None,
                       postseq=None, bgcor=False, double_freq=False)
    ct2.measure_keysight()

    bla

if 0: # Cavity T2E
    from single_cavity import cavT2
    detune = 5e3
    ct2 = cavT2.CavT2(qubit_info, cavity_infoB, .7, np.linspace(0, 500e3, 41), detune=detune, echo=True, seq=None,
                       postseq=None, bgcor=False)
    ct2.measure_keysight()
    bla

if 0: #interleaaved 01 and 02 cavity T2
    from single_cavity import CavT2_02
    from single_cavity import cavT2
    fig = plt.figure()
    fig.add_subplot(211)
    residual = fig.add_subplot(212)
    N = 1
    dig.set_trigger_period(2000)
    detune01 =10e3
        
    detune02 =20e3
    t201 = np.zeros(N)
    t202 = np.zeros(N)
    t201e = np.zeros(N)
    t202e = np.zeros(N)
    import time
    times01 = np.zeros(N)
    times02 = np.zeros(N)
    for i in range(N):
        # NOTE: Don't use more than 41 points or it gives garbage, still figureing out why
        dig.set_naverages(800)
        ct201 = cavT2.CavT2(qubit_info, cavity_infoA, .7, np.linspace(0, 500e3, 41), detune=detune01, seq=None,
                           postseq=None, bgcor=False, fig=fig)
        ct201.measure_keysight()
        t201[i] = ct201.fit_params['tau'].value
        t201e[i] = ct201.fit_params['tau'].stderr
        times01[i] = time.time()
        residual.cla()
    
        dig.set_naverages(1000)
        ct202 = CavT2_02.CavT2_02(qubit_info, cavity_infoA, .8, np.linspace(0, 300e3, 41), detune=detune02, seq=None,
                           postseq=None, bgcor=False, fig=fig)
        ct202.measure_keysight()
        t202[i] = ct202.fit_params['tau'].value
        t202e[i] = ct202.fit_params['tau'].stderr
        times02[i] = time.time()
        residual.cla()
    bla

    
if 0: # Cavity speco

    from single_cavity import cavspectroscopy
    cav_freq = 6086.78e6
    freq_range = .2e6
    cspec = cavspectroscopy.CavSpectroscopy(mclient.instruments['MXG'], qubit_info, cavity_infoB, [np.pi], 
                                            np.linspace(cav_freq-freq_range, cav_freq+freq_range, 51), plot_seqs=False)

    #This amplitude is NOT capped at 1 like on the qubit spec
    cspec.measure_keysight()
    bla


if 0: #SSB cavspec
    from single_cavity import ssbcavspec 
    cspec = ssbcavspec.SSBCavSpec(qubit_info, cavity_infoB, np.linspace(-2e6, 2e6, 61),
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
    seq = sequencer.Join([sequencer.Trigger(250), cA(0.561, 0), ges(2*np.pi, np.pi),
                          cA(-0.24, 0)]) # t2 seq test
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate(1, 0)])
    spec = ssbspec.SSBSpec(qubit_info, #np.linspace(-30e6, 10e6, 21),
                           np.linspace(-3e6, .5e6, 81),
#                           np.concatenate((
#                                           np.linspace(-22e6, -18e6, 15),
#                                           np.linspace(-7e6, -5e6, 25), 
#                                           np.linspace(-1e6, 1e6, 25)
#                                           )),
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
    for i in range(9):
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
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoB.rotate(1, 0), qubit_info.rotate(np.pi,0)])
#    postseq = qubit_info.rotate(np.pi/2,0)
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi/2, 0))
    spec = ssbspec.SSBSpec(ef_info, np.concatenate((
#                                                    np.linspace(-22e6, -18e6, 71),  
#                                                    np.linspace(-12e6, -8e6, 71),
                                                    np.linspace(-10e6, 1e6, 91),
                                                    )),
                           extra_info= [qubit_info, cavity_infoB],
                           seq =seq,  postseq = postseq, plot_seqs=False)
    spec.measure_keysight()
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
    for dt in [65]:
        
        seq = sequencer.Join([sequencer.Trigger(250), cB(.75, 0), ge(np.pi, 0), 
                              sequencer.Delay(dt), cB(.75, 0), ge(np.pi, 0)])        
#        seq = sequencer.Join([sequencer.Trigger(250), cB(.75, 0), sequencer.Delay(dt)])
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1, N=7, amaxx=None, Nx=None, amaxy=None, Ny=None,
                                   seq=seq, delay=0, saveas=None, bgcor=True)
        Qfun.measure_keysight()

#        seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, np.pi/2)])
#        seq.append(sequencer.Delay(dt))
#    disp = 1.5
#    for dt in np.linspace(210, 220, 1):
#        seq = sequencer.Join([sequencer.Trigger(500), 
#                          cB(disp, 0), ge(np.pi/2, 0), 
#                          sequencer.Delay(dt), 
#                          cB(disp, 0),
#                          geqs(np.pi, 0),
#                          cB(-disp, 0)
#                          ])
#        seq = sequencer.Join(seq)
#        seq = sequencer.Combined([seq, pulselib.Constant(seq.get_length(), 1, chan='3m1')])
#        Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1.75, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                     seq=seq, delay=0, saveas=None, bgcor=False, extra_info=ef_info, cav_switch='3m1')
#        Qfun.measure_keysight()
    bla

if 0: # make a cat 
    from scripts.single_cavity import Qfunction
#    seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, 0)])
#    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=2.5, N=21, amaxx=None, Nx=None, amaxy=None, Ny=None,
#             seq=seq, delay=0, saveas=None, bgcor=False, extra_info=ef_info)
#    Qfun.measure()
    
#        seq = sequencer.Join([sequencer.Trigger(250), cB(1.0, np.pi/2)])
#        seq.append(sequencer.Delay(dt))
    disp = 1
    seq = sequencer.Join([sequencer.Trigger(500), 
                      cB(disp, 0), ge(np.pi, 0), 
                      sequencer.Delay(65), 
                      cB(disp, 0),
                      geqs(np.pi, 0),
                      cB(-disp, 0)
                      ])
    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1.7, N=9, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=seq, delay=0, saveas=None, bgcor=True, extra_info=ef_info)
    Qfun.measure_keysight()

#    seq = sequencer.Join([sequencer.Trigger(250), ge(np.pi/2, 0), 
#                          cB(disp, 0), sequencer.Delay(300), cB(disp,0), 
#                          sequencer.Combined([geqs2(np.pi, 0), geqs(np.pi, 0)]), 
#                          cB(-disp-1.3,0)])
#    Qfun = Qfunction.QFunction(qubit_info, cavity_infoA, amax=1.2, N=13, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                 seq=seq, delay=0, saveas=None, bgcor=True, extra_info=ef_info)
#    Qfun.measure_keysight()
    
    
    bla


if 0: # Ramsey revival to calibrate wigner tomo
    from scripts.single_qubit import RamseyRevival
    seq = sequencer.Join([sequencer.Trigger(250), cB(1.5, 0)])
    rr = RamseyRevival.RamseyRevival(qubit_info, ef_info, np.linspace(0, 400, 81), 
                                     seq = seq, extra_info = cavity_infoB)
    rr.measure_keysight()

if 0: # Wigner function by displaced parity for cavity B
    from scripts.single_cavity import WignerbyParity
#    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
#                          geqs(pi,0), cB(-1.65, -pi*0.02)])
#    seq = sequencer.Join([sequencer.Trigger(250), cB(.5, 0)])
    disp = 1.5
    seq = sequencer.Join([sequencer.Trigger(500), 
                      cB(disp, 0), ge(np.pi/2, 0), 
                      sequencer.Delay(65), 
                      cB(disp, 0),
                      geqs(np.pi, 0),
                      cB(-disp, 0)
                      ])

    
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB,
                                         xs = np.linspace(-1.8,1.8,17), ys = np.linspace(-1.3,1.3,13),
                                         t_ge=70, t_gf=0,
                                         seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                         extra_info = None)
    Wfun.measure_keysight()

if 0: # Wigner function by displaced parity for cavity A
    from scripts.single_cavity import WignerbyParity
#    seq = sequencer.Join([prepareB, geph(pi/2,0), sequencer.Delay(950), cB(1.65, -pi*0.175),
#                          geqs(pi,0), cB(-1.65, -pi*0.02)])    
#    seq = sequencer.Join([sequencer.Trigger(250)])
    disp = 1.7
    seq = sequencer.Join([sequencer.Trigger(250), cA(disp, 0), 
                      ge(np.pi/2, 0), sequencer.Delay(270), cA(disp,0), 
                      geqs(np.pi, 0), 
                      cA(-disp,0)])
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoA,
                                         xs = np.linspace(-1.8,1.8,19), ys = np.linspace(-1.3,1.3,13),
                                         t_ge=270, t_gf=0,
                                         seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                         extra_info = None)
    Wfun.measure_keysight()


if 0: # Cavity cooling test
    from scripts.FWM import FWM_cavity_cooling
    freqs = np.linspace(-200.5e6, -199.5e6, 41)
#    freqs = np.array([200e6]*10)
    
    cc = FWM_cavity_cooling.FWM_cavity_cooling(qubit_info, cavity_infoA, cavity_infoR, freqs, .9, 
                 .9,1000e3)
    cc.measure_keysight()
    
    
    
