import mclient
import importlib
importlib.reload(mclient)
import numpy as np
from pulseseq import sequencer

alz = mclient.instruments['alazar']
fg = mclient.instruments['funcgen']
brick2 = mclient.instruments['brick2']
brick3 = mclient.instruments['brick3']
ag3 = mclient.instruments['ag3']
readout = mclient.instruments['readout']
alz = mclient.instruments['alazar']

if 1: # Load old settings.
    toload = ['readout','ag1_RO','brick1_LO','AWG1','AWG2','brick2','brick3','alazar','qubit1ge','qubit1ef','cavity1A','cavity1B']
    toload = ['AWG1']
    mclient.load_settings_from_file(r'c:\_data\settings\20150616\115752.set', toload)    # Last time-Rabi callibration
    bla

qubits = mclient.get_qubits()
readout_info = mclient.get_readout_info('readout')

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
cavity_infoA = mclient.get_qubit_info('cavity1A')
cavity_infoB = mclient.get_qubit_info('cavity1B')
#cavity_infoR = mclient.get_qubit_info('cavity1R')
#Qswitch_info1A = mclient.get_qubit_info('Qswitch1A')
#Qswitch_info1B = mclient.get_qubit_info('Qswitch1B')

from scripts.single_qubit import T2measurement, EFT2measurement, GFT2measurement, rabi, efrabi
from scripts.single_cavity import cavdisp, cavT2
efpi = sequencer.Sequence(ef_info.rotate(np.pi, 0))

if 0: # Calibrate qubit frequency (T2 Ramsey)
    alz.set_naverages(200)
    detune = 2000e3
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 8e3, 121), detune=detune, double_freq=False,
                                 postseq=efpi, extra_info=[ef_info,], singleshotbin=False)
    t2.measure()
    delta_qubit_freq = [int(t2.fit_params['freq'].value*1e6 - detune/1e3)*1e3]
    for i in range(2):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 8e3, 121), detune=detune, double_freq=False,
                                     generate=False, postseq=efpi, extra_info=[ef_info,])
        t2.measure()
        delta_qubit_freq.append(int(t2.fit_params['freq'].value*1e6 - detune/1e3)*1e3)
    qubit_freq = brick2.get_frequency()+qubit_info.deltaf + int(np.average(delta_qubit_freq)/1e3)*1e3
    brick2.set_frequency(qubit_freq-qubit_info.deltaf)

if 0: # Calibrate unselective ge pi and pi/2 pulses (power Rabi + pulse train)
    alz.set_naverages(400)
    tr0 = rabi.Rabi(qubit_info, np.linspace(-0.7, 0.7, 81), plot_seqs=False, update=False, seq=None,
                   postseq=efpi, selective=False, extra_info=[ef_info,])
    tr0.measure()
    tr = rabi.Rabi(qubit_info, np.linspace(tr0.pi_amp*0.97, tr0.pi_amp*1.05, 81), plot_seqs=False, update=True, seq=None,
                   postseq=efpi, selective=False, fit_type='PARABOLA', repeat_pulse=9, extra_info=[ef_info,])
    tr.measure()
    delta_pi_amp = tr.pi_amp - qubit_info.pi_amp
    tr = rabi.Rabi(qubit_info, np.linspace(tr0.pi_amp/2*0.96, tr0.pi_amp/2*1.04, 81), plot_seqs=False, update=True, seq=None,
                   postseq=efpi, selective=False, fit_type='PARABOLA', repeat_pulse=18, extra_info=[ef_info,])
    tr.measure()
    delta_pi2_amp = tr.pi2_amp - qubit_info.pi2_amp

if 0: # Calibrate selective and quasilective ge pi pulses
    alz.set_naverages(500)
    tr0 = rabi.Rabi(qubit_info, np.linspace(-0.02, 0.02, 81), plot_seqs=False, update=True, seq=None,
                   postseq=efpi, selective=1, extra_info=[ef_info,])
    tr0.measure()
    w_ratio = qubit_info.w_selective*1.0/qubit_info.w_quasilective
    tr = rabi.Rabi(qubit_info, np.linspace(tr0.pi_amp*w_ratio*0.92, tr0.pi_amp*w_ratio*1.08, 81), plot_seqs=False, update=True,
                   seq=None, postseq=efpi, selective=0.5, fit_type='PARABOLA', repeat_pulse=5, extra_info=[ef_info,])
    tr.measure()
    qubit_info = mclient.get_qubit_info(qubit_info.insname) # update all pi_amps in qubit_info container

if 1: # Calibrate ef frequency (ef T2 Ramsey)
    alz.set_naverages(300)
    detune = 2000e3
    eft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, np.linspace(0, 8e3, 121), detune=detune, double_freq=False)
    eft2.measure()
    delta_ef_freq = int(eft2.fit_params['freq'].value*1e6 - detune/1e3)*1e3
    ef_freq = brick2.get_frequency() + ef_info.deltaf + delta_ef_freq
    brick2.set_frequency(qubit_freq-qubit_info.deltaf)
    mclient.instruments[ef_info.insname].set_deltaf(ef_freq-brick2.get_frequency())
    ef_info.deltaf = ef_freq-brick2.get_frequency() # update ef frequency in container

if 0: # Calibrate ef pi pulses (ef power Rabi)
    alz.set_naverages(500)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, update=True, seq=None)
    efr.measure()
    ef_info = mclient.get_qubit_info(ef_info.insname) # update pi_amp in ef_info container

if 0: # Calibrate IQ_g and IQ_f (readout histogram)
    alz.set_naverages(40000)
    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], postseq=sequencer.Sequence(ef_info.rotate(np.pi,0)),
                   histogram=True, title='|f>', extra_info=[ef_info,])
    tr.measure()
    iqf = np.average(tr.shot_data[:])
    tr = rabi.Rabi(qubit_info, [0.00,], postseq=sequencer.Sequence(ef_info.rotate(np.pi,0)),
                   histogram=True, title='|g>', extra_info=[ef_info,])
    tr.measure()
    iqg = np.average(tr.shot_data[:])
    iqg_actual = iqg-(iqf-iqg)/88.0*3.0
    iqf_actual = iqf+(iqf-iqg)/88.0*9.0
    readout.set_IQe(iqf_actual)
    readout.set_IQg(iqg_actual)
    readout.set_IQe_radius(np.abs(iqf_actual-iqg_actual)/2*1.3)
    readout_info = mclient.get_readout_info('readout')

if 0: # Calibrate cavity displacements
    fg.set_frequency(100)
    alz.set_naverages(400)
    dispa = cavdisp.CavDisp(qubit_info, cavity_infoA, 2.5, 81, 0, seq=None, postseq=efpi,
                           delay=0, bgcor=False, update=True, extra_info=[ef_info,])
    dispa.measure()
    scale_cavA_amp = dispa.scaling
    dispb = cavdisp.CavDisp(qubit_info, cavity_infoB, 3.5, 81, 0, seq=None, postseq=efpi,
                           delay=0, bgcor=False, update=True, extra_info=[ef_info,])
    dispb.measure()
    scale_cavB_amp = dispb.scaling
    cavity_infoA = mclient.get_qubit_info(cavity_infoA.insname)
    cavity_infoB = mclient.get_qubit_info(cavity_infoB.insname) # update pi_amp in cavity containers

if 0: # Calibrate cavity frequencies (Snap T2)
    detune = 10e3
    ct2a = cavT2.CavT2(qubit_info, cavity_infoA, 1.0, np.linspace(0, 1.5e6, 101), detune=detune, seq=None,
                       postseq=efpi, bgcor=False, extra_info=[ef_info,])
    ct2a.measure()
    delta_cavA_freq = int(ct2a.fit_params['freq'].value*1e6 - detune/1e3)*1e3
    cavA_freq = ag3.get_frequency()+cavity_infoA.deltaf + delta_cavA_freq
    ag3.set_frequency(cavA_freq-cavity_infoA.deltaf)
    ct2b = cavT2.CavT2(qubit_info, cavity_infoB, 1.0, np.linspace(0, 1.5e6, 101), detune=10e3, seq=None,
                       postseq=efpi, bgcor=False, extra_info=[ef_info,])
    ct2b.measure()
    delta_cavB_freq = int(ct2b.fit_params['freq'].value*1e6 - detune/1e3)*1e3
    cavB_freq = brick3.get_frequency()+cavity_infoB.deltaf + delta_cavB_freq
    brick3.set_frequency(cavB_freq-cavity_infoB.deltaf)

for i in range(5): # Calibrate storage chi with ramsey revival
    alz.set_naverages(500)
    rr = T2measurement.T2Measurement(qubit_info, np.linspace(0, 10e3, 121), detune=10e3, double_freq=False,
                                     postseq=efpi, seq=None, extra_info=[cavity_infoA, ef_info,])
    rr.measure()
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate(2.0, 0)])
    rr = T2measurement.T2Measurement(qubit_info, np.linspace(0, 6e3, 121), detune=0e3, double_freq=False,
                                     postseq=efpi, seq=seq, extra_info=[cavity_infoA, ef_info,])
    rr.measure()
    alz.set_naverages(500)
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoB.rotate(2.0, 0)])
    rr = T2measurement.T2Measurement(qubit_info, np.linspace(0, 2e3, 121), detune=0e3, double_freq=False,
                                     postseq=efpi, seq=seq, extra_info=[cavity_infoB, ef_info,])
    rr.measure()

if 1: # Calibrate storage gf_chi with ramsey revival
    importlib.reload(GFT2measurement)
    alz.set_naverages(500)
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate(2.0, 0)])
    rr = GFT2measurement.GFT2Measurement(qubit_info, ef_info, np.linspace(0, 1.2e3, 121), detune=0e3, double_freq=False,
                                     postseq=efpi, seq=seq, extra_info=[cavity_infoA, ef_info,])
    rr.measure()
    alz.set_naverages(500)
    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoB.rotate(2.0, 0)])
    rr = GFT2measurement.GFT2Measurement(qubit_info, ef_info, np.linspace(0, 1.2e3, 121), detune=0e3, double_freq=False,
                                     postseq=efpi, seq=seq, extra_info=[cavity_infoB, ef_info,])
    rr.measure()

print('Qubit ge frequency shifted by %d kHz \n' % (np.average(delta_qubit_freq)/1000))
print('Qubit ef frequency shifted by %d kHz \n' % (delta_ef_freq/1000))
print('CavityA frequency shifted by %d kHz \n' % (delta_cavA_freq/1000))
print('CavityB frequency shifted by %d kHz \n' % (delta_cavB_freq/1000))

bla

if 1: # Set readout info
    iqg = 62.36+26.55j
    iqe = 9.43-3.31j
    iqg_actual = iqg-(iqe-iqg)/87.0*6.0
    iqe_actual = iqe+(iqe-iqg)/87.0*7.0
    readout.set_IQe(iqe_actual)
    readout.set_IQg(iqg_actual)
    readout.set_IQe_radius(np.abs(iqe_actual-iqg_actual)/2)

if 1:
    iqg = 5.60-11.30j
    iqe = 45.63-145.22j
    iqg_actual = iqg-(iqe-iqg)/88.0*5.0
    iqe_actual = iqe+(iqe-iqg)/88.0*7.0
    readout.set_IQe(iqe_actual)
    readout.set_IQg(iqg_actual)
    readout.set_IQe_radius(np.abs(iqe_actual-iqg_actual)/2)

if 1:
    readout.set_IQe(-39.4+36.7j)
    readout.set_IQg(-0.3-0.6j)
    readout.set_IQe_radius(30)

if 1: # High power readout
    ag1_RO=mclient.instruments['ag1_RO']
    brick1_LO=mclient.instruments['brick1_LO']
    ag1_RO.set_frequency(7686.44e6)
    brick1_LO.set_frequency(7736.44e6)
    ag1_RO.set_power(6.5)
    readout.set_pulse_len(500)

if 1: # Dispersive readout
    ag1_RO=mclient.instruments['ag1_RO']
    brick1_LO=mclient.instruments['brick1_LO']
    ag1_RO.set_frequency(7697.5e6)
    brick1_LO.set_frequency(7747.5e6)
    ag1_RO.set_power(-28)
    readout.set_IQe(0.61-0.28j)
    readout.set_IQg(3.43-0.52j)
    readout.set_pulse_len(1000)
