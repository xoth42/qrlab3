import matplotlib
matplotlib.interactive(True)
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as plt
from pulseseq import sequencer, pulselib
import matplotlib as mpl
#from t1t2_plotting import smart_T1_delays
import math as math

#mpl.rcParams['figure.figsize']=[5,3.5]
#mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']
VNA = mclient.instruments['VNA']


Yoko = mclient.instruments['Yoko']

if 1:
    from scripts.single_cavity import VNA_single_trace
#    rofreq = 7810e6
#    freq_range = 150e6
#    ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, np.linspace(10, 10, 1), np.linspace(rofreq-freq_range, rofreq+freq_range, 1001), qubit_pulse=False)
    ro = VNA_single_trace.SingleTrace(np.linspace(8e9, 8.2e9, 1601), use_async = False)#, meas_info = 'S21', device_info = 'circulator')
    ro.measure()
    plt.show()
    bla    



# Load old settings.
if 0:
    toload = ['AWG1','ag1','ag2', 'ag3' 'alazar', 'qFC14#1', 'eFC14#1','qubit_DO13#3', 'ef_DO13#3', 'qubit_DO13#4', 'ef_DO13#4']
    mclient.load_settings_from_file(r'c:\_data\settings\20131214\165409.set', toload)    # Last time-Rabi callibration
    bla

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('eFB14#1')
#cavity_info = mclient.get_qubit_info('cavity0')

#Find read-out cavity and choose a power
if 0: # Transmission
#    from scripts.single_cavity import rocavspectroscopy2
    from scripts.single_cavity import rocavspectroscopy
    rofreq = 7810e6
    freq_range = 150e6
    ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, np.linspace(10, 10, 1), np.linspace(rofreq-freq_range, rofreq+freq_range, 1001), qubit_pulse=False)
    ro.measure()
    plt.show()
    bla

#Find qubit
if 0: # Qubit spec
    from scripts.single_qubit import spectroscopy
#    from scripts.single_qubit import spectroscopy_IQ
    qubit_freq = 4281e6
    freq_range = 5e6
    spec = spectroscopy.Spectroscopy(mclient.instruments['brick1'], qubit_info,
                                     np.linspace(qubit_freq-freq_range, qubit_freq+freq_range, 80), [10],
                                     plen=20000, amp=0.001, plot_seqs=False) #1=1ns

#    spec = spectroscopy_IQ.Spectroscopy_IQ(client.instruments['gen'], qubit_info,
#                                     np.linspace(702e6, 710e6, 81), [-30],
#                                    plen=250*100, amp=0.1, ssb=False, plot_seqs=False)

    spec.measure()
    plt.show()
    bla
#the parameters are qubit_info, qubit frequency and readout power. Qubit drive power can be changed by changing AWG amp or the total pulse length. Pulse length=is plen*100ns

"""Qubit SSBspec"""
if 0: # Qubit SSBspec
    from scripts.single_qubit import ssbspec
    seq = sequencer.Trigger(250)
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 5e6, 101), seq=seq, plot_seqs=False)
    spec.measure()
    bla

"""Power Rabi -- Pi pulse calibration"""
if 1: # Calibrate pi pulse

    for i in range(1):
        from scripts.single_qubit import rabi
        alz.set_naverages(100000)
        tr = rabi.Rabi(qubit_info, np.linspace(0, 0.4, 11), plot_seqs=False, generate=True,
                       update=False)

#        from scripts.single_qubit import rabi_IQ
#        tr = rabi_IQ.Rabi(qubit_info, np.linspace(0, 0.5, 101), plot_seqs=False, real_signals=False)
        data=tr.measure()
    bla    

if 0: # Cavity spec
    from scripts.single_cavity import cavspectroscopy
    cav_freq = 9221.640e6
    cspec = cavspectroscopy.CavSpectroscopy(mclient.instruments['brick1'], qubit_info, cavity_info, [0.05], np.linspace(cav_freq-1e6, cav_freq+1e6, 81))
    cspec.measure()


if 0: # SSB cavspec
    from scripts.single_cavity import ssbcavspec
    cspec = ss
    bcavspec.SSBCavSpec(qubit_info, cavity_info, np.linspace(-0.5e6, 0.5e6, 101))
    cspec.measure()


if 0: # Qubit EFspec
    from scripts.single_qubit import spectroscopy
    ef_freq = 6240.94e6
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    spec = spectroscopy.Spectroscopy(mclient.instruments['brick1'], ef_info, np.linspace(ef_freq-5e6, ef_freq+5e6, 81), [19],
                                     plen=250, amp=0.5,
                                     seq=seq, postseq=postseq,
                                     extra_info=qubit_info, plot_seqs=False)
    spec.measure()
    bla

if 0: # EF rabi
    from scripts.single_qubit import efrabi
    alz.set_naverages(2000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(0, 1, 81), plot_seqs=False)
    efr.measure()
    period = efr.fit_params['period'].value

    alz.set_naverages(10000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(0, 1, 81), first_pi=False, force_period= period)
    efr.measure()


#EF rabi_QP and laser in CW
if 0:
#    from scripts.single_qubit import efrabi_QP
    from scripts.single_qubit import efrabi_laser
    laser_info = mclient.instruments['laserfg']
    laser_info.set_function('PULS')
    laser_info.set_Vhigh(1.5)
    laser_info.set_Vlow(0)
    laser_info.burst_mode()
    laser_info.set_output_on(True)
    pulse = 500e-6
    plen = pulse
    laser_info.set_pulsewidth(plen)
    edge = 1e-6
    laser_info.set_edgetime(edge)

    for delay in np.concatenate((np.linspace(0.3e6,plen*1e9, 3), np.linspace(plen*1e9,plen*1e9+400e3, 4),np.linspace(plen*1e9+400e3, plen*1e9+3e6, 4))):
#    for delay in [0.4e6, 0.8e6, 1e6, 2e6, 3e6]:
        if delay < 1.5e6:
            alz.set_naverages(1500)
            fg.set_frequency(400)
        else:
            alz.set_naverages(1000)
            fg.set_frequency(200)

        efr = efrabi_laser.EFRabi_laser(qubit_info, ef_info, np.linspace(0, 1, 81), laser_delay= delay)
#        efr = efrabi_QP.EFRabi_QP(qubit_info, ef_info, np.linspace(0, 1, 81), QP_delay= delay, inj_len = 30e3)
        efr.measure()
        period = efr.fit_params['period'].value
#        raibup_amp = efr.fit_params['amplitude'].value
#        rabiup_amp_err = efr.fit_params['amplitude'].stderr

        if delay < 1.5e6:
            alz.set_naverages(10000)
            fg.set_frequency(400)
        else:
            alz.set_naverages(10000)
            fg.set_frequency(200)

#        efr = efrabi_QP.EFRabi_QP(qubit_info, ef_info, np.linspace(0, 1, 81), QP_delay=delay, first_pi=False, inj_len = 30e3, force_period= period)
        efr = efrabi_laser.EFRabi_laser(qubit_info, ef_info, np.linspace(0, 1, 81), laser_delay=delay, first_pi=False, force_period= period)
        efr.measure()
#        raibnoup_amp = efr.fit_params['amplitude'].value
#        rabinoup_amp_err = efr.fit_params['amplitude'].stderr


if 0: # Mixer calibration:
    from scripts.single_qubit import mixer_calibration
    mixer_cal = mixer_calibration.Mixer_Calibration

    cal = mixer_cal('qGB14#2',7764e6, 'VA', 'AWG1', verbose=True,
                        base_amplitude= 3,
                        va_lo='brick3') # The frequency is the targeted lower sideband frequency, not the carrier

    cal.prep_instruments(reset_offsets=True, reset_ampskew=True)
    cal.tune_lo(mode='coarse')
    cal.tune_osb(mode=(0.5, 2000, 3, 1))
    cal.tune_lo(mode='fine') # useful if using 10 dB attenuation;
                            # LO leakage may creep up during osb tuning

    # this function will set the correct qubit_info sideband phase for use in experiments
    #    i.e. combines the AWG skew with the  7036.120e6current sideband phase offset
    cal.set_tuning_parameters(set_sideband_phase=True)
    cal.load_test_waveform()
    cal.print_tuning_parameters()
    bla


if 0: # Check histogramming
    from scripts.single_qubit import timerabi
    tr = timerabi.TimeRabi(qubit_info, [qubit_info.pi_area,], histogram=True, title='|e>')
    tr.measure()
    tr = timerabi.TimeRabi(qubit_info, [0.001,], histogram=True, title='|g>')
    tr.measure()
    tr = timerabi.TimeRabi(qubit_info, [qubit_info.pi_area/2,], histogram=True, title='|g>+|e>')
    tr.measure()

if 0: # T1
    from scripts.single_qubit import T1measurement

    t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 2000, 21), np.linspace(2100, 40e3, 41))), double_exp=False)
    t1.measure()
    bla

if 0:
    ''' Come on, please don't add complicated stuff to the plain T1 testing script.  Start somewhere else'''
    from scripts.single_qubit import T1measurement
#    laserfg.set_DCOffset(0)
#    for laserV in [0,1.5,2.0,2.1,2.2]:
#    for laserV in [0]:
#        laserfg.set_DCOffset(laserV)
    for rep_rate in [1000, 500, 200]:
        fg.set_frequency(rep_rate)
        for i in range(1):
            t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 20e3, 41), np.linspace(21e3, 100e3, 81))), double_exp=False)
#            if laserV <= 2:
#                t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 20e3, 31), np.linspace(20e3, 200e3, 51))), double_exp=False)
#            elif laserV <= 2.1:
#                t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 10e3, 31), np.linspace(10e3, 70e3, 51))), double_exp=False)
#            elif laserV <= 2.4:
#                t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 5e3, 31), np.linspace(5e3, 40e3, 51))), double_exp=False)
#            else:
#                t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 2e3, 31), np.linspace(2e3, 15e3, 51))), double_exp=False)
#            if laserV <= 2.3:
#                t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 20e3, 31), np.linspace(20e3, 70e3, 51))), double_exp=False)
#            else:
#                t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 10e3, 31), np.linspace(10e3, 40e3, 51))), double_exp=False)

   #        delays = np.linspace(0, 80e3, 81)
    #        t1 = T1measurement.T1Measurement(qubit_info, delays, double_exp=False)
            #t1.data.set_attrs(repRate='200kHz')
            t1.measure()



if 0: # T1_QP
    from scripts.single_qubit import T1measurement_QP
    for delays in [0.2e6, 0.1e6, 0.125e6, 0.15e6, 0.175e6, 0.2e6, 0.25e6]:
        t1 = T1measurement_QP.T1Measurement_QP(qubit_info, np.linspace(0, 10e3, 101), QP_delay=delays, inj_len=30e3)
        t1.measure()
    bla

if 0: # T2
    from scripts.single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 5000, 51), detune=2e6, double_freq=False)
    t2.measure()
    bla


if 0: # T2_QP
    from scripts.single_qubit import T2measurement_QP
    t2 = T2measurement_QP.T2Measurement_QP(qubit_info, np.linspace(0.3e3, 30e3, 100), QP_delay=1.5e6, detune=250e3, double_freq=False, inj_len=100e3, echotype = T2measurement_QP.ECHO_HAHN)
    t2.measure()
    bla

if 1: # T2echo
    from scripts.single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(100, 2000, 51), detune=2e6, echotype = T2measurement.ECHO_HAHN, plot_seqs = False)
    t2.measure()
    bla

if 0: # FT1
    from scripts.single_qubit import FT1measurement
    ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 160e3, 81))
    ft1.measure()

if 0: # EFT2
    from scripts.single_qubit import EFT2measurement # frequency stability of |f> vs |e>
    eft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, np.linspace(0.5e3, 50e3, 161), detune=300e3, double_freq=False, plot_seqs = False, echotype = EFT2measurement.ECHO_HAHN)
    eft2.measure()

if 0: # GFT2
    from scripts.single_qubit import GFT2measurement # frequency stability of |f> vs |g> # Echo does not work
    gft2 = GFT2measurement.GFT2Measurement(qubit_info, ef_info, np.linspace(0, 50e3, 161), detune=300e3, double_freq=False, plot_seqs = False, echotype = EFT2measurement.ECHO_HAHN)
    gft2.measure()

if 0: # Number splitting:
    from scripts.single_qubit import spectroscopy
    seq = sequencer.Join([sequencer.Trigger(250), cavity_info.rotate(np.pi, 0)])
#    postseq = sequencer.Sequence([sequencer.Trigger(250), cavity_info.rotate(np.pi, 0)])
    qubit_freq = 6306.770e6
    spec = spectroscopy.Spectroscopy(mclient.instruments['brick2'], qubit_info, np.linspace(qubit_freq-8e6, qubit_freq+2e6, 101), [11.5],
                                     plen=6000, seq = seq, amp=0.09, extra_info=cavity_info, plot_seqs=True)
    spec.measure()


if 0: # SSB number splitting:
    from scripts.single_qubit import ssbspec
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_info.rotate(np.pi, 0)])
#    cav_pulse = sequencer.Combined([
#                    sequencer.Constant(1000, 1, chan="3m2"),
#                    ])
#    seq = sequencer.Join([sequencer.Trigger(250), cav_pulse])
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(50000, 1, chan="3m2")])

    for i in range (100):
        spec = ssbspec.SSBSpec(qubit_info, np.concatenate((np.linspace(-2.5e6, -1.5e6, 20),np.linspace(-1.48e6, -0.80e6, 81), np.linspace(-0.75e6, 1.5e6, 45))),
                               seq=None, extra_info=cavity_info, plot_seqs=False)
        spec.measure()
#    for coplay_delay in [12000]:
#        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-3e6, 2e6, 121),
#                           seq=None, extra_info=cavity_info, plot_seqs=False, coplay_delay=coplay_delay)
#        spec.measure()

if 0: # Cavity lifetime:
    from scripts.single_cavity import cavT1
    t1 = cavT1.CavT1(qubit_info, cavity_info, np.pi, np.linspace(0, 30e3, 101), proj_num=0, seq=None, extra_info=None, bgcor=False,
                     plot_seqs=False)
    t1.measure()

if 0:
    from scripts.single_qubit import rabi_QP
    tr = rabi_QP.Rabi_QP(qubit_info, np.linspace(0, 1, 81), QP_delay = 10e3, inj_len = 30e3)
    tr.measure()

#test laser pulse
if 0:
    from scripts.single_qubit import lasertest
    laser_info = mclient.instruments['laserfg']
    for plen in [20e-6, 50e-6, 100e-6]:
        laser_info.set_pulsewidth(plen)
        blah = lasertest.Rabi_laser(qubit_info, np.linspace(0, 1, 81), laser_plen=250, laser_delay = (5e-6))
        blah.measure()

#for number splitting and cavity lifetime using a laser injection
if 0:
    from scripts.single_qubit import ssbspec
#    laser_info.set_output_on(True)
#    laser_delay = 50e3
#    plen = 10-6
#    laser_info.set_pulsewidth(plen)
#    edge = 5e-6
#    laser_info.set_edgetime(edge)

#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(250, 1, '1m2'), sequencer.Delay(laser_delay)])

    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-6e6, 3e6, 121),
                           extra_info=cavity_info, plot_seqs=False)
    spec.measure()
#    laser_info.set_output_on(False)


if 0:
#for i in range(20):
    tau=[]
    tau_err=[]
    delays=[]
    freq=[]
    freq_err=[]
    T2=[]
    T2_err=[]
    from scripts.single_qubit import T1measurement_laser
#    from scripts.single_qubit import T2measurement_laser
    laser_info = mclient.instruments['laserfg']
    laser_info.set_function('PULS')
    laser_info.set_Vhigh(1.5)
    laser_info.set_Vlow(0)
    laser_info.burst_mode()
    laser_info.set_output_on(True)
#    for pulse in[10e-6, 50e-6, 100e-6, 250e-6, 400e-6]:
    for j in range(3):
        pulse = 500e-6
        plen = pulse
        laser_info.set_pulsewidth(plen)
        edge = 1e-6
        laser_info.set_edgetime(edge)
        for add_delay in np.concatenate((np.linspace(plen*1e9,plen*1e9+400e3, 4),np.linspace(plen*1e9+400e3, plen*1e9+3e6, 4))):
#        for add_delay in  np.linspace(plen*1e9,plen*1e9+100e3, 26):
    #    for add_delay in [5e3, 10e3, 50e3, 100e3, 250e3, 500e3, 750e3, 900e3, 1e6, 1.2e6, 1.5e6, 2.5e6, 5e6]:
            delays.append(add_delay)

#            rep_rate = 1/(plen  + 3e-3)
#            rep_rate=100.0*floor(rep_rate/100.0)
    #        rep_rate = 1/(10e-3)
    #        fg.set_frequency(500)
    #        add_delay = 10e3
#
            if add_delay < 50e3:
                fg.set_frequency(250)
                alz.set_naverages(1000)
                t1_range = np.concatenate((np.linspace(0, 10e3, 41), np.linspace(11e3, 20e3, 41)))
#                t1_range = np.concatenate((np.linspace(0, 4e3, 41), np.linspace(4.5e3, 10e3, 41)))
            elif add_delay < 100e3:
                fg.set_frequency(250)
                alz.set_naverages(1000)
                t1_range = np.linspace(0, 10e3, 41)
            elif add_delay < plen*1e9:
                fg.set_frequency(250)
                alz.set_naverages(1000)
                t1_range = np.linspace(0, 2e3, 81)
#                t1_range = np.concatenate((np.linspace(0, 5e3, 41), np.linspace(6e3, 10e3, 41)))
            elif add_delay < plen*1e9 + 200e3:
                fg.set_frequency(250)
                alz.set_naverages(1000)
                t1_range = np.linspace(0, 3e3, 81)
            elif add_delay < plen*1e9 + 400e3:
                fg.set_frequency(200)
                alz.set_naverages(1000)
                t1_range = np.linspace(0, 6e3, 81)

            elif add_delay < plen*1e9 + 1.1e6:
                fg.set_frequency(200)
                alz.set_naverages(1000)
                t1_range = np.linspace(0, 40e3, 81)
            else:
                fg.set_frequency(200)
                alz.set_naverages(400)
                t1_range = np.concatenate((np.linspace(0, 10e3, 41), np.linspace(11e3, 20e3, 41)))

            #t1 = T1measurement_laser.T1Measurement_laser(qubit_info, t1_range, double_exp=False, laser_plen=250, laser_delay = (plen*1e9 + 1.7*edge*1e9 + add_delay))
            t1 = T1measurement_laser.T1Measurement_laser(qubit_info, t1_range, double_exp=False, laser_plen=250, laser_delay = add_delay)
            tau_new, tau_new_err = t1.measure()
            t1.data.set_attrs(post_inj_delay = add_delay)
            t1.data.set_attrs(injection_length = plen)
            plt.close()
            tau.append(tau_new)
            tau_err.append(tau_new_err)
            plt.figure(1)
            plt.clf()
#            plt.errorbar(np.array(delays)/1000.0, np.array(tau)/1000.0, np.array(tau_err)/1000.0, fmt ='mo')
            plt.errorbar(np.array(range(len(tau))),np.array(tau)/1000.0, np.array(tau_err)/1000.0, fmt ='mo')
#            plt.axis(xmin=min(delays)*0.9/1000.0, xmax=max(delays)*1.10/1000.0)
            #plt.semilogx()
            plt.title('QP Decay After Optical Injection')
            plt.xlabel('Iterations - from 0 to 100 us after inj end')
            plt.ylabel('T1 (us)')

#            t2 = T2measurement_laser.T2Measurement_laser(qubit_info, t1_range/2.0, detune= 20.0e9/max(t1_range), laser_plen=250, laser_delay = (plen*1e9 + 1.7*edge*1e9 + add_delay))
#            t2 = T2measurement_laser.T2Measurement_laser(qubit_info, t1_range/8.0, detune= 80.0e9/max(t1_range), laser_plen=250, laser_delay = (plen*1e9 + 1.7*edge*1e9 + add_delay))
#            freq_new, freq_new_err, T2_new, T2_new_err = t2.measure()
#            t2.data.set_attrs(post_inj_delay = add_delay)
#            t2.data.set_attrs(injection_length = plen)
#            plt.close()
#            T2.append(T2_new)
#            T2_err.append(T2_new_err)
#            plt.figure(2)
#            plt.clf()
#            plt.errorbar(np.array(delays)/1000.0, np.array(T2)/1000.0, np.array(T2_err)/1000.0, fmt ='b^')
#            plt.axis(xmin=min(delays)*0.9/1000.0, xmax=max(delays)*1.10/1000.0)
#            plt.figure(3)
#            plt.clf()
##            delta_freq = freq_new*1e6 - 20e9/max(t1_range)/1e3 #delta_freq is in kHz
#            delta_freq = freq_new*1e6 - 80e9/max(t1_range)/1e3
#            freq.append(delta_freq)
#            freq_err.append(freq_new_err*1e6)
#            plt.errorbar(np.array(delays)/1000.0, np.array(freq), np.array(freq_err), fmt ='g^')
#            plt.axis(xmin=min(delays)*0.9/1000.0, xmax=max(delays)*1.10/1000.0)

    laser_info.set_output_on(False)

#QP decay with laser:
if 0:
    from scripts.single_qubit import QPdecay_laser
    laser_info = mclient.instruments['laserfg']
    laser_info.set_output_on(True)
    eff_T1_delay = 500.0
    meas_per_QPinj = 4
    meas_per_reptime = 10
    fg = mclient.instruments['funcgen']
    rep_time=1.0e9/fg.get_frequency()
    laser_inj_len = 50e-6
    laser_info.set_pulsewidth(laser_inj_len)
    edge = 5e-6
    laser_info.set_edgetime(edge)
    T1_delays = smart_T1_delays(T1_int=45.0e3, QPT1=0.4e6, half_decay_point=0.2e6, eff_T1_delay=eff_T1_delay, probe_point=0.7, meas_per_QPinj=meas_per_QPinj, meas_per_reptime=meas_per_reptime)

    for i in range(5):
        alz.set_naverages(4000)
        qpd = QPdecay_laser.QPdecay_laser(qubit_info, T1_delays, rep_time, meas_per_reptime, meas_per_QPinj, fit_start=5, vg=0.0, ve=6.75, eff_T1_delay=eff_T1_delay, inj_len= laser_inj_len*1e9)
        qpd.measure()
#        ag3 = mclient.instruments['ag3']
#        qpd.data.set_attrs(inj_power=ag3.get_power())

        T1_delays = (T1_delays -np.log(0.5)*1000.0/qpd.invT1 - eff_T1_delay)/2.0
        for j, delay in enumerate(T1_delays):
            if delay < 0:
                T1_delays[j]=0.0

    laser_info.set_output_on(False)

"""
Quasi-particle Decay
"""
if 0: # QPDecay
#    from scripts.single_qubit import T1measurement
    from scripts.single_qubit import QPdecay
    eff_T1_delay = 500.0
    meas_per_QPinj = 40
    meas_per_reptime = 5
    fg = mclient.instruments['funcgen']
    rep_time=1.0e9/fg.get_frequency()

    T1_delays = smart_T1_delays(T1_int=6.0e3, QPT1=5.0e6, half_decay_point=3.0e6, eff_T1_delay=eff_T1_delay, probe_point=0.5, meas_per_QPinj=meas_per_QPinj, meas_per_reptime=meas_per_reptime)
    for i in range(5):
        alz.set_naverages(4000)
        qpd = QPdecay.QPdecay(qubit_info, T1_delays, rep_time, meas_per_reptime, meas_per_QPinj, fit_start=6, vg=0.0, ve=3.8, eff_T1_delay=eff_T1_delay, inj_len=360e3)
        qpd.measure()
        ag3 = mclient.instruments['ag3']
        qpd.data.set_attrs(inj_power=ag3.get_power())

        T1_delays = (T1_delays -np.log(0.5)*1000.0/qpd.invT1 - eff_T1_delay)/2.0
        for j, delay in enumerate(T1_delays):
            if delay < 0:
                T1_delays[j]=0.0

#        alz.set_naverages(2000)
#        t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 100e3, 81), np.linspace(100e3, 200e3, 81))), double_exp=False)
#        t1.measure()


if 0:
    from scripts.single_qubit import T2measurement
    from scripts.single_qubit import QPdecayRamsey
    fg = mclient.instruments['funcgen']
    rep_time=1.0e9/fg.get_frequency()
    T2_delay = 22500 #ns
    for i in range(5):
        alz.set_naverages(25000)
        qpd = QPdecayRamsey.QPdecayRamsey(qubit_info, T2_delay=T2_delay, detune=200e3, rep_time=rep_time, meas_per_reptime=1, meas_per_QPinj=400, fit_start=5, vg=0, ve=4.25, inj_len=100e3)
        qpd.measure()
        alz.set_naverages(8000)
        t2e = T2measurement.T2Measurement(qubit_info, np.linspace(0.3e3, 40e3, 100), detune=200e3, echotype = T2measurement.ECHO_HAHN)
        t2e.measure()
