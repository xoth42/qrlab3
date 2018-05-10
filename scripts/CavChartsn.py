import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer

alz = mclient.instruments['alazar']
fg = mclient.instruments['funcgen']
laserfg = mclient.instruments['laserfg']
awg2 = mclient.instruments['AWG2']
ag1 = mclient.instruments['ag1_RO']

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#cavity_infoR = mclient.get_qubit_info('cavity1R')
cavity_infoA = mclient.get_qubit_info('cavity1A')
cavity_infoB = mclient.get_qubit_info('cavity1B')
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
ef = ef_info.rotate
efs= ef_info.rotate_selective
efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))



'''
Qswitchseq = sequencer.Join([sequencer.Repeat(sequencer.Delay(100), 100),
            sequencer.Combined([
            sequencer.Repeat(sequencer.Constant(1000, 0.5, chan=Qswitch_info1A.sideband_channels[0]), 500),
            sequencer.Repeat(sequencer.Constant(1000, 0.5, chan=Qswitch_info1A.sideband_channels[1]), 500),
#            Repeat(Constant(250, 1, chan=5), 800),      # Qubit/Readout master switch
            ])])
'''
if 0: # Cavity disp calibration
    from scripts.single_cavity import cavdisp
#    prepareAE = sequencer.Join([sequencer.Trigger(250), ge(np.pi, 0)])
    disp = cavdisp.CavDisp(qubit_info, cavity_infoB, 3.5, 81, 0, seq=None,
                           delay=0, bgcor=False, update=False, generate=True,
#                           Qswitch_infoA=Qswitch_infoB, Qswitch_infoB=Qswitch_infoB,
#                           extra_info=[Qswitch_infoA, Qswitch_infoB,],
                          )
    disp.measure()
    bla

if 0: # Cavity T1:
    from scripts.single_cavity import cavT1
    for i in range(2):
        t1 = cavT1.CavT1(qubit_info, cavity_infoA, 2.0, np.linspace(1e3, 9.5e6, 101), proj_num=0, seq=None,
                         postseq=efpi, bgcor=False, extra_info=[ef_info,])
        t1.measure()

if 0:# Cavity T2
    from scripts.single_cavity import cavT2
    detune = 10e3
    ct2a = cavT2.CavT2(qubit_info, cavity_infoA, 1.0, np.linspace(0, 1.0e6, 81), detune=detune, seq=None,
                       postseq=efpi, bgcor=False, extra_info=[ef_info,])
    ct2a.measure()

    for i in range(10):
        t2 = cavT2.CavT2(qubit_info, cavity_infoA, 1.0, np.linspace(0, 1.0e6, 101), detune=10e3, seq=None,
                         postseq=efpi, bgcor=False, extra_info=[ef_info,])
        t2.measure()
    bla

if 0: #SSB cavspec
    from scripts.single_cavity import ssbcavspec
    cspec = ssbcavspec.SSBCavSpec(qubit_info, cavity_infoB, np.linspace(-5.0e6, 5.0e6, 101),
                                  postseq=efpi, extra_info=[ef_info,])
    cspec.measure()
    bla

if 0: # Measure cavity photon population
    from scripts.single_qubit import rabi
    tr = rabi.Rabi(qubit_info, np.linspace(-0.005, 0.005, 81), plot_seqs=False, update=False, seq=None, selective=1, singleshotbin=True)
    period = tr.fit_params['period'].value
    alz.set_naverages(4000)
    tr = rabi.Rabi(qubit_info, np.linspace(-0.005, 0.005, 81), plot_seqs=False, update=False, seq=None, selective=1, singleshotbin=True, fix_period=period)
    tr.measure()

if 0: #Sideband modulated number splitting:
    from scripts.single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoB.rotate(0.6, 0)])
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-3.5e6, 0.5e6, 101),
                           extra_info= cavity_infoB,
                           seq = seq,  plot_seqs=False)
    spec.measure()
    bla

if 1: #EF Sideband modulated number splitting:
    from scripts.single_qubit import ssbspec
    seq = sequencer.Join([sequencer.Trigger(250), qubit_info.rotate(np.pi,0), cavity_infoA.rotate(1.2, 0)])
    postseq = qubit_info.rotate(np.pi,0)
#    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-5e6, 1e6, 121),
                           extra_info= [qubit_info, cavity_infoA],
                           seq =seq,  postseq = postseq, plot_seqs=False)
    spec.measure()
    bla

if 0: #mixer calibration:
    from scripts.single_qubit import mixer_calibration
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
    for delay in [100,200,300,400,500]:
        seq = sequencer.Join([sequencer.Trigger(250), c(1.0, 0), ge(np.pi,0), ef(np.pi,0), sequencer.Delay(delay), ef(-np.pi,0), ge(-np.pi, 0)])
        Qfun = Qfunction.QFunction(qubit_info1, cavity_info1A, amax=2.5, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, delay=0, saveas=None, bgcor=False, extra_info=ef_info1)
        Qfun.measure()
    bla

