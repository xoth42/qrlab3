import mclient
import importlib
importlib.reload(mclient)
import numpy as np
from pulseseq import sequencer
import matplotlib as mpl
import math as math


mpl.rcParams['figure.figsize']=[5,3.5]
#mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']
alz = mclient.instruments['alazar']
fg = mclient.instruments['funcgen']
laserfg = mclient.instruments['laserfg']

# Load old settings.
if 0:
    toload = ['readout','ag1_RO','brick1_LO','AWG1','AWG2','brick2','brick3','alazar','qubit1ge','qubit1ef','cavity1A','cavity1B']
    mclient.load_settings_from_file(r'c:\_data\settings\20150608\151238.set', toload)    # Last time-Rabi callibration
    bla

#qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
#gf_info1 = mclient.get_qubit_info('Qubit1gf')
#cavity_infoA = mclient.get_qubit_info('cavity1A')
#cavity_infoB = mclient.get_qubit_info('cavity1B')
#Qswitch_infoA = mclient.get_qubit_info('Qswitch1A')
#Qswitch_infoB = mclient.get_qubit_info('Qswitch1B')
#Qswitch_infoR = mclient.get_qubit_info('Qswitch1R')

#qubit_info2 = mclient.get_qubit_info('qDblCoax2')
#cavity_info2A = mclient.get_qubit_info('cavity2A')
#cavity_info2B = mclient.get_qubit_info('cavity2B')

# Find read-out cavity and choose a power
if 0:
    from scripts.single_cavity import rocavspectroscopy
    rofreq = 8.574e9#7685.90e6#7685.90e6
    freq_range = 2e6
#    seq = sequencer.Sequence([sequencer.Trigger(250), cavity_info1A.rotate(2, 0), cavity_info1B.rotate(2, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info1.rbit_info,otate(np.pi, 0), ef_info1.rotate(np.pi, 0)])
    ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, np.linspace(-34, -30, 1), np.linspace(rofreq-freq_range, rofreq+freq_range, 51),
                                             qubit_pulse=False, seq=None)
    ro.measure()
    bla

#Find qubit
if 1:
    from scripts.single_qubit import spectroscopy
 #   from scripts.single_qubit import spectroscopy_IQ
    qubit_freq = 4498e6
    freq_range = 12e6
#    seq = sequencer.Sequence([sequencer.Trigger(250), ef_info.rotate(np.pi, 0)])
    spec = spectroscopy.Spectroscopy(mclient.instruments['brick1'], qubit_info, 
                                 np.linspace(qubit_freq-freq_range, qubit_freq+freq_range, 51), [-34],
                                 plen=20000, amp=.025, seq=None, plot_seqs=True) #1=1ns5
#    spec = spectroscopy_IQ.Spectroscopy_IQ(client.instruments['gen'], qubit_info,
#                                     np.linspace(702e6, 710e6, 81), [-30],
#                                    plen=250*100, amp=0.1, ssb=False, plot_seqs=False)
    spec.measure()
    bla

if 0: #SSB spec
    from scripts.single_qubit import ssbspec
#    seq = sequencer.Sequence([sequencer.Trigger(250), cavity   _info1B.rotate(1, 0)])
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 5e6, 101),  plot_seqs=False,
                           seq=None, generate=True, singleshotbin=False)
    spec.measure()
    bla

if 0: # cavity spectroscopy
    from scripts.single_cavity import cavspectroscopy
    cav_freq = 5533.302e6
    cspec = cavspectroscopy.CavSpectroscopy(mclient.instruments['brick3'], qubit_info, cavity_infoB,
                                            [0.1], np.linspace(cav_freq-5e6, cav_freq+5e6, 101), Qswitchseq=None)
    cspec.measure()
    bla

if 0: # pump tone spectroscopy
    from scripts.single_cavity import cavspectroscopy
    cav_freq = 4319.660100e6#7976.85e6
    seq = sequencer.Join([sequencer.Delay(10000),
            sequencer.Combined([
            Qswitch_infoA.rotate(np.pi, 0),    # 250us square pulse pump
            Qswitch_infoB.rotate(np.pi, 0),
            Qswitch_infoR.rotate(np.pi, 0),      # Qubit/Readout master switch
            ]), sequencer.Delay(20000)])
    cspec = cavspectroscopy.CavSpectroscopy(mclient.instruments['ag3'], qubit_info, cavity_infoB,
                                            [1.2], np.linspace(cav_freq-25e6, cav_freq+25e6, 81),
                                            Qswitchseq=seq, extra_info=[Qswitch_infoA, Qswitch_infoB, Qswitch_infoR])
    cspec.measure()
    bla

if 0: #Find qubit ef
    from scripts.single_qubit import spectroscopy
    ef_freq = 4959.00e6
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    spec = spectroscopy.Spectroscopy(mclient.instruments['ag3'], ef_info, np.linspace(ef_freq-5e6, ef_freq+5e6, 101), [-32],
                                     plen=2000, amp=0.004,
                                     seq=seq, postseq=postseq,
                                     extra_info=qubit_info, plot_seqs=False)
    spec.measure()
    bla