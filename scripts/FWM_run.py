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

#os.chdir(r'C:/qrlab/scripts')
dig = mclient.instruments['dig']

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#cavity_infoR = mclient.get_qubit_info('cavity1R')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#cavity_infoB = mclient.get_qubit_info('cavityBob')
#fwm_info1 = mclient.get_qubit_info('fwm_info1')
#fwm_info2 = mclient.get_qubit_info('fwm_info2')
#Qswitch_info1A = mclient.get_qubit_info('Qswitch1A')
#Qswitch_info1B = mclient.get_qubit_info('Qswitch1B')

#qubit_info2 = mclient.get_qubit_info('qDblCoax2')
#ef_info2 = mclient.get_qubit_info('eDblCoax2')
#cavity_info2A = mclient.get_qubit_info('cavity2A')
#cavity_info2B = mclient.get_qubit_info('cavity2B')

#cA = cavity_infoA.rotate
#cB = cavity_infoB.rotate
ge = qubit_info.rotate
ges= qubit_info.rotate_selective
#ef = ef_info.rotate
#efs= ef_info.rotate_selective
#efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))



if 0: # q func test
    from scripts.single_cavity import Qfunction
    Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=1, N=10, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 seq=None, delay=0, saveas=None, bgcor=False)
    Qfun.measure_keysight()

if 0: # fwm spec
    import FWM_spec
    fwm_gen = mclient.instruments['PumpBrick']
    target = 5063.3e6 - 100e6 + 67e6 - 11.0258e6#5.219e9
#    target = 5.02602e9
    for power in [.1]:
        spec = FWM_spec.FWM_spec(qubit_info, cavity_infoA, fwm_info1, fwm_gen, 2.5, 
                                 750e3, np.linspace(target-1e6, target+1e6, 11), power, 
                                 '4m1', plot_seqs=False, bgcor=False)
        spec.measure()
#        spec = FWM_spec.FWM_spec(qubit_info, cavity_infoA, fwm_info1, fwm_gen, 2, 
#                         800e3, np.linspace(target-.2e6, target+.2e6, 101), power, 
#                         '4m1', plot_seqs=False, bgcor=False)
#        spec.measure()

if 0: # abt mixing
    os.chdir(r'C:/qrlab/scripts/FWM/')
    import FWM_abt
    xvec = np.linspace(-1, 1, 3)
#    abt = FWM_abt.FWM_abt(qubit_info, cavity_infoA, cavity_infoB, fwm_info, 100, 
#                          np.linspace(-1, 1, 10), np.linspace(-1, 1, 10), seq=None,
#                          generate=True, plot_seqs = True)
    abt = FWM_abt.FWM_abt(qubit_info, cavity_infoA, cavity_infoA, fwm_info, 
                          xvec, xvec, 0, which_cavity = 'b', seq=None, saveas=None, 
                          plot_seqs=True, generate = True)
    abt.measure_keysight()

if 0: #spec to find cavity stark shift
    import FWM_SSBCavSpec
    spec = FWM_SSBCavSpec.FWM_SSBCavSpec(qubit_info, cavity_infoA, fwm_info1, 
                                         1000, .5, np.linspace(-10e6, 2e6, 21),
                                         plot_seqs = True)
    spec.measure_keysight()


if 0: # f0 - g1 fwm test
    fwm_gen = mclient.instruments['SCpump']
#    target = 4.96386e9 * 2 - 221.2e6 - 6.92618e9   this is original set values (juliang)
#    target = 4.96356e9 * 2 - 221.2e6 + 6.92618e9    4.96356e9 is the frequency at the center
#    target = 6.926e9
    target = 4.96320e9 * 2 - 221.2e6 - 6.92605e9
#    freqs = np.linspace(target-3e6, target+3e6, 50)    this is original set values (juliang)
    freqs = np.linspace(target-3.0e6, target +4.0e6, 101)
    import FWM_f0g1
    for amp in [.035]:
        f0g1 = FWM_f0g1.FWM_f0g1(qubit_info, ef_info, fwm_gen, 5e3, 
                     freqs, 15, amp, '2m1')
        f0g1.measure()
        
        
if 1: # f0 - g1 time domain test
    fwm_gen = mclient.instruments['SCpump']
    delays = np.linspace(0, 6e3, 151)
    import FWM_f0g1_t1
    for amp in [.035]:
        f0g1 = FWM_f0g1_t1.FWM_f0g1_t1(qubit_info, ef_info, fwm_gen, delays, 
                     amp, '2m1', plot_seqs = False)
        f0g1.measure_keysight()

