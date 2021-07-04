import mclient
import importlib
importlib.reload(mclient)
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
#from pulseseq import sequencer, pulselib

#mpl.rcParams['figure.figsize']=[6,4]

fg = mclient.instruments['funcgen']
alz = mclient.instruments['alazar']
brick2 = mclient.instruments['brick2']
ag3 = mclient.instruments['ag3']
readout_info = mclient.instruments['readout']
laser_info = mclient.instruments['laserfg']

field = 0.0
temp = 'cd'

################################################################################################################################################
from scripts.single_qubit import T1measurement, T2measurement
from scripts.single_qubit import T1measurement_QP, T2measurement_QP
from scripts.single_qubit import FT1measurement, EFT2measurement, GFT2measurement
from scripts.single_qubit import efrabi
from scripts.single_qubit import efrabi_QP
from scripts.single_qubit import QPdecay
from scripts.single_qubit import rabi

def try_twice(func, N=2, **kwargs):
    for i in range(N):
        try:
            return func(**kwargs)
        except Exception as e:
            print('Error %s' % (e,))
            pass
    print('Failed to do %s %s times...' % (func, N))

def calibrate_IQ(qubit_info, n_avg):
    alz.set_naverages(n_avg)
    IQg = readout_info.get_IQg()
    IQe = readout_info.get_IQe()
    vproj = IQe - IQg
    vproj /= np.abs(vproj) # '/=' means vproj = vproj/np.abs(vproj)

    histoE = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], real_signals=False, histogram=True, title='|e>')
    histoE.measure()
    plt.close()
    ys = np.average(histoE.shot_data[:])
    ys = ys - IQg
    ve = np.real(ys) * vproj.real  + np.imag(ys) * vproj.imag
    histoG = rabi.Rabi(qubit_info, [0.0,], real_signals=False, histogram=True, title='|g>')
    histoG.measure()
    plt.close()
    ys = np.average(histoG.shot_data[:])
    ys = ys - IQg
    vg = np.real(ys) * vproj.real  + np.imag(ys) * vproj.imag
    return ve, vg

def do_T1(qubit_info, delays, QP_injection_delay, QP_injection_length, laser_power):
    if QP_injection_delay == None:
        t1 = T1measurement.T1Measurement(qubit_info, delays, laser_power = laser_power)
    else:
        t1 = T1measurement_QP.T1Measurement_QP(qubit_info, delays, QP_injection_delay, QP_injection_length)
        t1.data.set_attrs(inj_power=ag3.get_power())
    t1.data.set_attrs(field_current=field)
    t1.data.set_attrs(temperature=temp)
#    t1.data.set_attrs(laser_power=voltage)
    t1.measure()
    plt.close()
    return t1

def do_T1_plot(qubit_info, n_avg, delays, t1_fits, fig_num, QP_injection_delay=None, QP_injection_length=10e3, laser_power = None):
    alz.set_naverages(n_avg)
    t1 = do_T1(qubit_info, delays, QP_injection_delay, QP_injection_length, laser_power)
    if t1!=None and QP_injection_delay is None:
        t1_fits['t1s'].append(t1.fit_params['tau'].value/1000.0)
        t1_fits['t1s_err'].append(t1.fit_params['tau'].stderr/1000.0)
        t1_fits['ofs'].append(t1.fit_params['ofs'].value)
        t1_fits['amps'].append(t1.fit_params['amplitude'].value)
        plt.figure(fig_num)
        plt.clf()
        plt.axis(xmin=-len(t1_fits['t1s'])*0.10, xmax=len(t1_fits['t1s'])*1.10)
        plt.errorbar(list(range(len(t1_fits['t1s']))),t1_fits['t1s'],t1_fits['t1s_err'],fmt='go')
        plt.xlabel("Measurement iterations")
        plt.ylabel("T1(us)")
#       plt.semilogy()\
    if t1!=None and QP_injection_delay is not None:
        t1_fits['t1s_QP'].append(t1.fit_params['tau'].value/1000.0)
        t1_fits['t1s_QP_err'].append(t1.fit_params['tau'].stderr/1000.0)
        plt.figure(fig_num)
        plt.clf()
        plt.axis(xmin=-len(t1_fits['t1s_QP'])*0.10, xmax=len(t1_fits['t1s_QP'])*1.10)
        plt.errorbar(list(range(len(t1_fits['t1s_QP']))),t1_fits['t1s_QP'],t1_fits['t1s_QP_err'], fmt ='go')
        plt.xlabel("QPdelay")
        plt.ylabel("T1(us)")


def smart_T1_delays(T1_int=90e3, QPT1=1.5e6, half_decay_point=1e6, eff_T1_delay=800.0, probe_point=0.5, meas_per_QPinj=30, meas_per_reptime=5):
    """
    T1_int = 90e3                  # Intrinsic T1 of the qubit
    QPT1 = 1.5e6                    # Guess the lifetime of the quasiparticles
    half_decay_point = 1e6        # The QP_delay time that would make qubit relax halfway to ground state with T1_delay=0, i.e. relax during readout pulse
    eff_T1_delay = 800.0            # The effective T1_delay due to the finite length of the readout pulse, usually taken as readout pulse length/2
    """
#    rep_time = 1.0e9/fg.get_frequency()
#    T1_QPref = 1/(np.log(2)/eff_T1_delay-1/T1_int)      # T1 at half decay point = effective readout delay/ln(2), excluding intrinsic part giving the T1 due to quasiparticles
#    n_delayless = int(half_decay_point/rep_time)           # Number of points with T1_delay = 0
#
##    QP_times_s = np.linspace(rep_time, half_decay_point, n_delayless)
#    T1_delays_s = np.linspace(0, 0, n_delayless)
#    QP_times_l = np.linspace(half_decay_point+rep_time, meas_per_QPinj*rep_time, meas_per_QPinj-n_delayless)
#    T1_delays_l = np.log(2)/(1/T1_int+1/T1_QPref*np.exp(-(QP_times_l-half_decay_point)/QPT1))-eff_T1_delay
##    QP_times = np.concatenate((QP_times_s, QP_times_l))
#    T1_delays = np.concatenate((T1_delays_s, T1_delays_l))

    rep_time = 1.0e9/fg.get_frequency()
    n_points = meas_per_QPinj * meas_per_reptime
    step_time = rep_time / meas_per_reptime
    T1_QPref = 1/(np.log(2)/eff_T1_delay-1/T1_int)      # T1 at half decay point = effective readout delay/ln(2), excluding intrinsic part giving the T1 due to quasiparticles

    QP_times = np.linspace(0, (n_points-1)*step_time, n_points)
    T1_est = 1/(1/T1_int+1/T1_QPref*np.exp(-(QP_times-half_decay_point)/QPT1))
    T1_delays = -np.log(probe_point)*T1_est-eff_T1_delay
    for j, delay in enumerate(T1_delays):
        if delay < 0:
            T1_delays[j]=0.0
    return T1_delays

def do_QPdecay(qubit_info, T1_delay, **kwargs):
    rep_time = 1e9/fg.get_frequency()
    qpd = QPdecay.QPdecay(qubit_info, T1_delay, rep_time, **kwargs)
    qpd.data.set_attrs(field_current=field)
    qpd.data.set_attrs(temperature=temp)
#    qpd.data.set_attrs(T1_delay=T1_delay)
    qpd.data.set_attrs(inj_power=ag3.get_power())
#    qpd.data.set_attrs(laser_voltage=laser_info.get_DCOffset())
#    qpd.measure()
#    plt.close()
    return qpd

def do_QPdecay_plot(qubit_info, n_avg, T1_delay, qpd_fits, fig_num, **kwargs):
    alz.set_naverages(n_avg)
    ag3.set_rf_on(True)
    qpd = do_QPdecay(qubit_info, T1_delay, **kwargs)
    qpd.measure()
    plt.close()
    if qpd!=None:
        qpd_fits['qpt1s'].append(qpd.fit_params['tau'].value/1000.0)
        qpd_fits['qpt1s_err'].append(qpd.fit_params['tau'].stderr/1000.0)
        qpd_fits['qpofs'].append(qpd.fit_params['ofs'].value)
        qpd_fits['qpofs_err'].append(qpd.fit_params['ofs'].stderr)
#        qpd_fits['amps'].append(qpd.fit_params['amplitude'].value)
    qpofs_array = np.array(qpd_fits['qpofs'])
    qpofs_err_array = np.array(qpd_fits['qpofs_err'])
    plt.figure(fig_num)
    plt.clf()
    plt.subplot(211).axis(xmin=-len(qpd_fits['qpt1s'])*0.10, xmax=len(qpd_fits['qpt1s'])*1.10)#, ymin=0, ymax=1)
    plt.errorbar(list(range(len(qpd_fits['qpt1s']))),qpd_fits['qpt1s'],qpd_fits['qpt1s_err'],fmt='go')
    plt.ylabel("Tau QP(ms)")
    plt.subplot(212).axis(xmin=-len(np.array(qpd_fits['qpofs']))*0.10, xmax=len(np.array(qpd_fits['qpofs']))*1.10)#, ymin=10, ymax=30)
    plt.errorbar(list(range(len(qpofs_array))), 1/qpofs_array, qpofs_err_array/qpofs_array/qpofs_array, fmt='b^')
    plt.xlabel("Measurement iterations")
    plt.ylabel("Qubit T1-floor(us)")
    ag3.set_rf_on(False)
    return qpd


def do_T2(qubit_info, delays, detune, double_freq=False, QP_injection_delay=None, QP_injection_length=10e3, laser_power = None):
    if QP_injection_delay == None:
        t2 = T2measurement.T2Measurement(qubit_info, delays, detune=detune, double_freq=double_freq, laser_power = laser_power)
    else:
        t2 = T2measurement_QP.T2Measurement_QP(qubit_info, delays, QP_delay=QP_injection_delay, detune=detune, double_freq=double_freq, inj_len=QP_injection_length)
        t2.data.set_attrs(QP_delay=QP_injection_delay)
    t2.data.set_attrs(field_current=field)
    t2.data.set_attrs(temperature=temp)
#    t2.data.set_attrs(laser_power=voltage)
    t2.measure()
    plt.close()
    return t2

def do_T2_plot(qubit_info, n_avg, delays, detune, t2_fits, fig_num, double_freq=False, QP_injection_delay=None, QP_injection_length=10e3, laser_power = None):
    alz.set_naverages(n_avg)
    t2 = do_T2(qubit_info, delays, detune, double_freq, QP_injection_delay, QP_injection_length, laser_power)
    if (t2!=None):
        t2_fits['t2s'].append(t2.fit_params['tau'].value/1000)
        t2_fits['t2s_err'].append(t2.fit_params['tau'].stderr/1000.0)
        t2_fits['t2freqs'].append(t2.fit_params['freq'].value*1000 - detune/1e6)
        t2_fits['t2freqs_err'].append(t2.fit_params['freq'].stderr*1000.0)
        t2_fits['amps'].append(t2.fit_params['amp'].value)
        t2_fits['amps_err'].append(t2.fit_params['amp'].stderr)
        if double_freq == True:
            t2_fits['t22s'].append(t2.fit_params['tau2'].value/1000)
            t2_fits['t22s_err'].append(t2.fit_params['tau2'].stderr/1000.0)
            t2_fits['t22freqs'].append(t2.fit_params['freq2'].value*1000 -detune/1e6)
            t2_fits['t22freqs_err'].append(t2.fit_params['freq2'].stderr*1000.0)
            t2_fits['amp2s'].append(t2.fit_params['amp2'].value)
            t2_fits['amp2s_err'].append(t2.fit_params['amp2'].stderr)
        if QP_injection_delay is not None:
            t2_fits['t2s_QP'].append(t2.fit_params['tau'].value/1000)
            t2_fits['t2s_QP_err'].append(t2.fit_params['tau'].stderr/1000.0)
            t2_fits['t2freqs_QP'].append(t2.fit_params['freq'].value*1000 -detune/1e6)
            t2_fits['t2freqs_QP_err'].append(t2.fit_params['freq'].stderr*1000.0)
#            t2_fits['amps_QP'].append(t2.fit_params['amp'].value)
#            t2_fits['amps_QP_err'].append(t2.fit_params['amp'].stderr)

    if double_freq == False and QP_injection_delay is None:
        plt.figure(fig_num)
        plt.clf()
        plt.subplot(211).axis(xmin=-len(t2_fits['t2s'])*0.10, xmax=len(t2_fits['t2s'])*1.10, ymin= min(t2_fits['t2s'])*0.7, ymax=max(t2_fits['t2s'])*1.3)
        plt.errorbar(list(range(len(t2_fits['t2s']))),t2_fits['t2s'],t2_fits['t2s_err'],fmt='rs')
        plt.ylabel("T2(us)")
        plt.subplot(212).axis(xmin=-len(t2_fits['t2freqs'])*0.10, xmax=len(t2_fits['t2freqs'])*1.10, ymin=min(t2_fits['t2freqs'])-0.02, ymax=max(t2_fits['t2freqs'])+0.02)
        plt.errorbar(list(range(len(t2_fits['t2freqs']))),t2_fits['t2freqs'],t2_fits['t2freqs_err'],fmt='b^')
        plt.xlabel("Measurement iterations")
        plt.ylabel("Ramsey Freq.(MHz) (= Actual Qubit Freq. - Drive Freq.)")
    if double_freq == False and QP_injection_delay is not None:
        plt.figure(fig_num)
        plt.clf()
        plt.subplot(211).axis(xmin=-len(t2_fits['t2s_QP'])*0.10, xmax=len(t2_fits['t2s_QP'])*1.10, ymin= min(t2_fits['t2s_QP'])*0.7, ymax=max(t2_fits['t2s_QP'])*1.3)
        plt.errorbar(list(range(len(t2_fits['t2s_QP']))),t2_fits['t2s_QP'],t2_fits['t2s_QP_err'],fmt='rs')
        plt.ylabel("T2 with QP injection (us)")
        plt.subplot(212).axis(xmin=-len(t2_fits['t2freqs_QP'])*0.10, xmax=len(t2_fits['t2freqs_QP'])*1.10, ymin= min(min(t2_fits['gft2freqs']),min(t2_fits['t22freqs']))-0.02, ymax=max(max(t2_fits['t2freqs']), max(t2_fits['t22freqs']))+0.02)
        plt.errorbar(list(range(len(t2_fits['t2freqs_QP']))),t2_fits['t2freqs_QP'],t2_fits['t2freqs_QP_err'],fmt='b^')
        plt.xlabel("Measurement iterations")
        plt.ylabel("Ramsey Freq.(MHz) (= Actual Qubit Freq. - Drive Freq.)")
    if double_freq is True:
        plt.figure(fig_num)
        plt.clf()
        plt.subplot(311).axis(xmin=-len(t2_fits['t2s'])*0.10, xmax=len(t2_fits['t2s'])*1.10, ymin= min(t2_fits['t2s'])*0.7, ymax=max(t2_fits['t22s'])*1.3)
        plt.errorbar(list(range(len(t2_fits['t2s']))),t2_fits['t2s'],t2_fits['t2s_err'],fmt='rs')
        plt.errorbar(list(range(len(t2_fits['t22s']))),t2_fits['t22s'],t2_fits['t22s_err'],fmt='b^')
        plt.ylabel("T2(us)")
        plt.subplot(312).axis(xmin=-len(t2_fits['t2freqs'])*0.10, xmax=len(t2_fits['t2freqs'])*1.10,ymin= min(min(t2_fits['t2freqs']),min(t2_fits['t22freqs']))-0.02, ymax=max(max(t2_fits['t2freqs']), max(t2_fits['t22freqs']))+0.02)
        plt.errorbar(list(range(len(t2_fits['t2freqs']))),t2_fits['t2freqs'],t2_fits['t2freqs_err'],fmt='rs')
        plt.errorbar(list(range(len(t2_fits['t22freqs']))),t2_fits['t22freqs'],t2_fits['t22freqs_err'],fmt='b^')
        plt.ylabel("Ramsey Freq.(MHz) (= Actual Qubit Freq. - Drive Freq.)")
        plt.subplot(313).axis(xmin=-len(t2_fits['amps'])*0.10, xmax=len(t2_fits['amps'])*1.10,ymin= min(t2_fits['amp2s'])*0.8, ymax=max(t2_fits['amps'])*1.2)
        plt.errorbar(list(range(len(t2_fits['amps']))),t2_fits['amps'],t2_fits['amps_err'],fmt='rs')
        plt.errorbar(list(range(len(t2_fits['amp2s']))),t2_fits['amp2s'],t2_fits['amp2s_err'],fmt='b^')
        plt.xlabel("Measurement iterations")
        plt.ylabel("Amplitudes (AU)")

#    plt.semilogy()

def do_T2echo(qubit_info, delays, detune, laser_power = None):
    t2e = T2measurement.T2Measurement(qubit_info, delays, detune, echotype=T2measurement.ECHO_HAHN, laser_power = laser_power, title='T2 Echo')
    t2e.data.set_attrs(field_current=field)
    t2e.data.set_attrs(temperature=temp)
#    t2e.data.set_attrs(laser_power=voltage)
    t2e.measure()
    plt.close()
    return t2e

def do_T2echo_plot(qubit_info, n_avg, delays, detune, t2E_fits, fig_num, laser_power = None):
    alz.set_naverages(n_avg)
    t2e = do_T2echo(qubit_info, delays, detune, laser_power = laser_power)
    if t2e!=None:
        t2E_fits['t2es'].append(t2e.fit_params['tau'].value/1000)
        t2E_fits['t2es_err'].append(t2e.fit_params['tau'].stderr/1000)
    plt.figure(fig_num)
    plt.clf()
    plt.axis(xmin=-len(t2E_fits['t2es'])*0.10, xmax=len(t2E_fits['t2es'])*1.10, ymin= min(t2E_fits['t2es'])*0.8, ymax=max(t2E_fits['t2es'])*1.2)
    plt.errorbar(list(range(len(t2E_fits['t2es']))),t2E_fits['t2es'],t2E_fits['t2es_err'],fmt='mv') # magenta color and v-shape markers
    plt.xlabel("Measurement iterations")
    plt.ylabel("T2Echo(us)")

def do_FT1(qubit_info, ef_info, delays):
    ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, delays)
    ft1.data.set_attrs(field_current=field)
    ft1.data.set_attrs(temperature=temp)
    ft1.measure()
    plt.close()
    return ft1

def do_FT1_plot(qubit_info, ef_info, n_avg, delays, ft1_fits, fig_num):
    alz.set_naverages(n_avg)
    ft1 = do_FT1(qubit_info, ef_info, delays)
    if ft1!=None:
        ft1_fits['ft1s'].append(ft1.fit_params['tau'].value/1000.0)
        ft1_fits['ft1s_err'].append(ft1.fit_params['tau'].stderr/1000.0)
        ft1_fits['ofs'].append(ft1.fit_params['ofs'].value)
        ft1_fits['amps'].append(ft1.fit_params['amplitude'].value)
    plt.figure(fig_num)
    plt.clf()
    plt.axis(xmin=-len(ft1_fits['ft1s'])*0.10, xmax=len(ft1_fits['ft1s'])*1.10, ymin= min(ft1_fits['ft1s'])*0.8, ymax=max(ft1_fits['ft1s'])*1.2)
    plt.errorbar(list(range(len(ft1_fits['ft1s']))),ft1_fits['ft1s'],ft1_fits['ft1s_err'],fmt='go')
    plt.xlabel("Measurement iterations")
    plt.ylabel("FT1(us)")

def do_EFT2(qubit_info, ef_info, delays, detune, double_freq=False, QP_injection_delay=None, QP_injection_length=10e3):
    eft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, delays, detune=detune, double_freq=double_freq)
    eft2.data.set_attrs(field_current=field)
    eft2.data.set_attrs(temperature=temp)
    eft2.measure()
    plt.close()
    return eft2

def do_EFT2_plot(qubit_info, ef_info, n_avg, delays, detune, ft2_fits, fig_num, double_freq=False, QP_injection_delay=None, QP_injection_length=10e3, laser_power = None):
    alz.set_naverages(n_avg)
    eft2 = do_EFT2(qubit_info, ef_info, delays, detune, double_freq, QP_injection_delay, QP_injection_length)
    if (eft2!=None):
        ft2_fits['eft2s'].append(eft2.fit_params['tau'].value/1000)
        ft2_fits['eft2s_err'].append(eft2.fit_params['tau'].stderr/1000.0)
        ft2_fits['eft2freqs'].append(eft2.fit_params['freq'].value*1000 - detune/1e6)
        ft2_fits['eft2freqs_err'].append(eft2.fit_params['freq'].stderr*1000.0)
        ft2_fits['eft2amps'].append(eft2.fit_params['amp'].value)
        ft2_fits['eft2amps_err'].append(eft2.fit_params['amp'].stderr)
        if double_freq == True:
            ft2_fits['eft22s'].append(eft2.fit_params['tau2'].value/1000)
            ft2_fits['eft22s_err'].append(eft2.fit_params['tau2'].stderr/1000.0)
            ft2_fits['eft22freqs'].append(eft2.fit_params['freq2'].value*1000 -detune/1e6)
            ft2_fits['eft22freqs_err'].append(eft2.fit_params['freq2'].stderr*1000.0)
            ft2_fits['eft2amp2s'].append(eft2.fit_params['amp2'].value)
            ft2_fits['eft2amp2s_err'].append(eft2.fit_params['amp2'].stderr)
        if QP_injection_delay is not None:
            ft2_fits['eft2s_QP'].append(eft2.fit_params['tau'].value/1000)
            ft2_fits['eft2s_QP_err'].append(eft2.fit_params['tau'].stderr/1000.0)
            ft2_fits['eft2freqs_QP'].append(eft2.fit_params['freq'].value*1000 -detune/1e6)
            ft2_fits['eft2freqs_QP_err'].append(eft2.fit_params['freq'].stderr*1000.0)

    if double_freq == False and QP_injection_delay is None:
        plt.figure(fig_num)
        plt.clf()
        plt.subplot(211).axis(xmin=-len(ft2_fits['eft2s'])*0.10, xmax=len(ft2_fits['eft2s'])*1.10, ymin= min(ft2_fits['eft2s'])*0.7, ymax=max(ft2_fits['eft2s'])*1.3)
        plt.errorbar(list(range(len(ft2_fits['eft2s']))),ft2_fits['eft2s'],ft2_fits['eft2s_err'],fmt='rs')
        plt.ylabel("EFT2(us)")
        plt.subplot(212).axis(xmin=-len(ft2_fits['eft2freqs'])*0.10, xmax=len(ft2_fits['eft2freqs'])*1.10, ymin=min(ft2_fits['eft2freqs'])-0.02, ymax=max(ft2_fits['eft2freqs'])+0.02)
        plt.errorbar(list(range(len(ft2_fits['eft2freqs']))),ft2_fits['eft2freqs'],ft2_fits['eft2freqs_err'],fmt='b^')
        plt.xlabel("Measurement iterations")
        plt.ylabel("Ramsey Freq.(MHz) (= Actual Qubit Freq. - Drive Freq.)")
    if double_freq == False and QP_injection_delay is not None:
        plt.figure(fig_num)
        plt.clf()
        plt.subplot(211).axis(xmin=-len(ft2_fits['eft2s_QP'])*0.10, xmax=len(ft2_fits['eft2s_QP'])*1.10, ymin= min(ft2_fits['eft2s_QP'])*0.7, ymax=max(ft2_fits['eft2s_QP'])*1.3)
        plt.errorbar(list(range(len(ft2_fits['eft2s_QP']))),ft2_fits['eft2s_QP'],ft2_fits['eft2s_QP_err'],fmt='rs')
        plt.ylabel("EFT2 with QP injection (us)")
        plt.subplot(212).axis(xmin=-len(ft2_fits['eft2freqs_QP'])*0.10, xmax=len(ft2_fits['eft2freqs_QP'])*1.10, ymin=min(ft2_fits['eft2freqs_QP'])-0.02, ymax=max(ft2_fits['eft2freqs_QP'])+0.02)
        plt.errorbar(list(range(len(ft2_fits['eft2freqs_QP']))),ft2_fits['eft2freqs_QP'],ft2_fits['eft2freqs_QP_err'],fmt='b^')
        plt.xlabel("Measurement iterations")
        plt.ylabel("Ramsey Freq.(MHz) (= Actual Qubit Freq. - Drive Freq.)")
    if double_freq is True:
        plt.figure(fig_num)
        plt.clf()
        plt.subplot(311).axis(xmin=-len(ft2_fits['eft2s'])*0.10, xmax=len(ft2_fits['eft2s'])*1.10, ymin= min(ft2_fits['eft2s'])*0.7, ymax=max(ft2_fits['eft22s'])*1.3)
        plt.errorbar(list(range(len(ft2_fits['eft2s']))),ft2_fits['eft2s'],ft2_fits['eft2s_err'],fmt='rs')
        plt.errorbar(list(range(len(ft2_fits['eft22s']))),ft2_fits['eft22s'],ft2_fits['eft22s_err'],fmt='b^')
        plt.ylabel("EFT2(us)")
        plt.subplot(312).axis(xmin=-len(ft2_fits['eft2freqs'])*0.10, xmax=len(ft2_fits['eft2freqs'])*1.10,ymin= min(min(ft2_fits['eft2freqs']),min(ft2_fits['eft22freqs']))-0.02, ymax=max(max(ft2_fits['eft2freqs']), max(ft2_fits['eft22freqs']))+0.02)
        plt.errorbar(list(range(len(ft2_fits['eft2freqs']))),ft2_fits['eft2freqs'],ft2_fits['eft2freqs_err'],fmt='rs')
        plt.errorbar(list(range(len(ft2_fits['eft22freqs']))),ft2_fits['eft22freqs'],ft2_fits['eft22freqs_err'],fmt='b^')
        plt.ylabel("Ramsey Freq.(MHz) (= Actual Qubit Freq. - Drive Freq.)")
        plt.subplot(313).axis(xmin=-len(ft2_fits['eft2amps'])*0.10, xmax=len(ft2_fits['eft2amps'])*1.10,ymin= min(ft2_fits['eft2amp2s'])*0.8, ymax=max(ft2_fits['eft2amps'])*1.2)
        plt.errorbar(list(range(len(ft2_fits['eft2amps']))),ft2_fits['eft2amps'],ft2_fits['eft2amps_err'],fmt='rs')
        plt.errorbar(list(range(len(ft2_fits['eft2amp2s']))),ft2_fits['eft2amp2s'],ft2_fits['eft2amp2s_err'],fmt='b^')
        plt.xlabel("Measurement iterations")
        plt.ylabel("Amplitudes (AU)")

def do_EFT2echo(qubit_info, ef_info, delays, detune, laser_power = None):
    eft2e = EFT2measurement.EFT2Measurement(qubit_info, ef_info, delays, detune, echotype=EFT2measurement.ECHO_HAHN, title='EFT2 Echo')
    eft2e.data.set_attrs(field_current=field)
    eft2e.data.set_attrs(temperature=temp)
#    t2e.data.set_attrs(laser_power=voltage)
    eft2e.measure()
    plt.close()
    return eft2e

def do_EFT2echo_plot(qubit_info, ef_info, n_avg, delays, detune, t2E_fits, fig_num, laser_power = None):
    alz.set_naverages(n_avg)
    eft2e = do_EFT2echo(qubit_info, ef_info, delays, detune, laser_power = laser_power)
    if eft2e!=None:
        t2E_fits['eft2es'].append(eft2e.fit_params['tau'].value/1000)
        t2E_fits['eft2es_err'].append(eft2e.fit_params['tau'].stderr/1000)
    plt.figure(fig_num)
    plt.clf()
    plt.axis(xmin=-len(t2E_fits['eft2es'])*0.10, xmax=len(t2E_fits['eft2es'])*1.10, ymin= min(t2E_fits['eft2es'])*0.8, ymax=max(t2E_fits['eft2es'])*1.2)
    plt.errorbar(list(range(len(t2E_fits['eft2es']))),t2E_fits['eft2es'],t2E_fits['eft2es_err'],fmt='mv') # magenta color and v-shape markers
    plt.xlabel("Measurement iterations")
    plt.ylabel("EFT2Echo(us)")

def do_GFT2(qubit_info, ef_info, delays, detune, double_freq=False, QP_injection_delay=None, QP_injection_length=10e3):
    gft2 = GFT2measurement.GFT2Measurement(qubit_info, ef_info, delays, detune=detune, double_freq=double_freq)
    gft2.data.set_attrs(field_current=field)
    gft2.data.set_attrs(temperature=temp)
    gft2.measure()
    plt.close()
    return gft2

def do_GFT2_plot(qubit_info, ef_info, n_avg, delays, detune, ft2_fits, fig_num, double_freq=False, QP_injection_delay=None, QP_injection_length=10e3, laser_power = None):
    alz.set_naverages(n_avg)
    gft2 = do_GFT2(qubit_info, ef_info, delays, detune, double_freq, QP_injection_delay, QP_injection_length)
    if (gft2!=None):
        ft2_fits['gft2s'].append(gft2.fit_params['tau'].value/1000)
        ft2_fits['gft2s_err'].append(gft2.fit_params['tau'].stderr/1000.0)
        ft2_fits['gft2freqs'].append(gft2.fit_params['freq'].value*1000 - detune/1e6)
        ft2_fits['gft2freqs_err'].append(gft2.fit_params['freq'].stderr*1000.0)
        ft2_fits['gft2amps'].append(gft2.fit_params['amp'].value)
        ft2_fits['gft2amps_err'].append(gft2.fit_params['amp'].stderr)
        if double_freq == True:
            ft2_fits['gft22s'].append(gft2.fit_params['tau2'].value/1000)
            ft2_fits['gft22s_err'].append(gft2.fit_params['tau2'].stderr/1000.0)
            ft2_fits['gft22freqs'].append(gft2.fit_params['freq2'].value*1000 -detune/1e6)
            ft2_fits['gft22freqs_err'].append(gft2.fit_params['freq2'].stderr*1000.0)
            ft2_fits['gft2amp2s'].append(gft2.fit_params['amp2'].value)
            ft2_fits['gft2amp2s_err'].append(gft2.fit_params['amp2'].stderr)
        if QP_injection_delay is not None:
            ft2_fits['gft2s_QP'].append(gft2.fit_params['tau'].value/1000)
            ft2_fits['gft2s_QP_err'].append(gft2.fit_params['tau'].stderr/1000.0)
            ft2_fits['gft2freqs_QP'].append(gft2.fit_params['freq'].value*1000 -detune/1e6)
            ft2_fits['gft2freqs_QP_err'].append(gft2.fit_params['freq'].stderr*1000.0)

    if double_freq == False and QP_injection_delay is None:
        plt.figure(fig_num)
        plt.clf()
        plt.subplot(211).axis(xmin=-len(ft2_fits['gft2s'])*0.10, xmax=len(ft2_fits['gft2s'])*1.10, ymin= min(ft2_fits['gft2s'])*0.7, ymax=max(ft2_fits['gft2s'])*1.3)
        plt.errorbar(list(range(len(ft2_fits['gft2s']))),ft2_fits['gft2s'],ft2_fits['gft2s_err'],fmt='ks')
        plt.ylabel("GFT2(us)")
        plt.subplot(212).axis(xmin=-len(ft2_fits['gft2freqs'])*0.10, xmax=len(ft2_fits['gft2freqs'])*1.10, ymin=min(ft2_fits['gft2freqs'])-0.02, ymax=max(ft2_fits['gft2freqs'])+0.02)
        plt.errorbar(list(range(len(ft2_fits['gft2freqs']))),ft2_fits['gft2freqs'],ft2_fits['gft2freqs_err'],fmt='c^')
        plt.xlabel("Measurement iterations")
        plt.ylabel("Ramsey Freq.(MHz) (= Actual Qubit Freq. - Drive Freq.)")
    if double_freq == False and QP_injection_delay is not None:
        plt.figure(fig_num)
        plt.clf()
        plt.subplot(211).axis(xmin=-len(ft2_fits['gft2s_QP'])*0.10, xmax=len(ft2_fits['gft2s_QP'])*1.10, ymin= min(ft2_fits['gft2s_QP'])*0.7, ymax=max(ft2_fits['gft2s_QP'])*1.3)
        plt.errorbar(list(range(len(ft2_fits['gft2s_QP']))),ft2_fits['gft2s_QP'],ft2_fits['gft2s_QP_err'],fmt='ks')
        plt.ylabel("GFT2 with QP injection (us)")
        plt.subplot(212).axis(xmin=-len(ft2_fits['gft2freqs_QP'])*0.10, xmax=len(ft2_fits['gft2freqs_QP'])*1.10, ymin=min(ft2_fits['gft2freqs_QP'])-0.02, ymax=max(ft2_fits['gft2freqs_QP'])+0.02)
        plt.errorbar(list(range(len(ft2_fits['gft2freqs_QP']))),ft2_fits['gft2freqs_QP'],ft2_fits['gft2freqs_QP_err'],fmt='c^')
        plt.xlabel("Measurement iterations")
        plt.ylabel("Ramsey Freq.(MHz) (= Actual Qubit Freq. - Drive Freq.)")
    if double_freq is True:
        plt.figure(fig_num)
        plt.clf()
        plt.subplot(311).axis(xmin=-len(ft2_fits['gft2s'])*0.10, xmax=len(ft2_fits['gft2s'])*1.10, ymin= min(ft2_fits['gft2s'])*0.7, ymax=max(ft2_fits['gft22s'])*1.3)
        plt.errorbar(list(range(len(ft2_fits['gft2s']))),ft2_fits['gft2s'],ft2_fits['gft2s_err'],fmt='ks')
        plt.errorbar(list(range(len(ft2_fits['gft22s']))),ft2_fits['gft22s'],ft2_fits['gft22s_err'],fmt='c^')
        plt.ylabel("GFT2(us)")
        plt.subplot(312).axis(xmin=-len(ft2_fits['gft2freqs'])*0.10, xmax=len(ft2_fits['gft2freqs'])*1.10,ymin= min(min(ft2_fits['gft2freqs']),min(ft2_fits['gft22freqs']))-0.02, ymax=max(max(ft2_fits['gft2freqs']), max(ft2_fits['gft22freqs']))+0.02)
        plt.errorbar(list(range(len(ft2_fits['gft2freqs']))),ft2_fits['gft2freqs'],ft2_fits['gft2freqs_err'],fmt='ks')
        plt.errorbar(list(range(len(ft2_fits['gft22freqs']))),ft2_fits['gft22freqs'],ft2_fits['gft22freqs_err'],fmt='c^')
        plt.ylabel("Ramsey Freq.(MHz) (= Actual Qubit Freq. - Drive Freq.)")
        plt.subplot(313).axis(xmin=-len(ft2_fits['gft2amps'])*0.10, xmax=len(ft2_fits['gft2amps'])*1.10,ymin= min(ft2_fits['gft2amp2s'])*0.8, ymax=max(ft2_fits['gft2amps'])*1.2)
        plt.errorbar(list(range(len(ft2_fits['gft2amps']))),ft2_fits['gft2amps'],ft2_fits['gft2amps_err'],fmt='ks')
        plt.errorbar(list(range(len(ft2_fits['gft2amp2s']))),ft2_fits['gft2amp2s'],ft2_fits['gft2amp2s_err'],fmt='c^')
        plt.xlabel("Measurement iterations")
        plt.ylabel("Amplitudes (AU)")

def do_GFT2echo(qubit_info, ef_info, delays, detune, laser_power = None):
    gft2e = GFT2measurement.GFT2Measurement(qubit_info, ef_info, delays, detune, echotype=EFT2measurement.ECHO_HAHN, title='GFT2 Echo')
    gft2e.data.set_attrs(field_current=field)
    gft2e.data.set_attrs(temperature=temp)
#    t2e.data.set_attrs(laser_power=voltage)
    gft2e.measure()
    plt.close()
    return gft2e

def do_GFT2echo_plot(qubit_info, ef_info, n_avg, delays, detune, t2E_fits, fig_num, laser_power = None):
    alz.set_naverages(n_avg)
    gft2e = do_GFT2echo(qubit_info, ef_info, delays, detune, laser_power = laser_power)
    if gft2e!=None:
        t2E_fits['gft2es'].append(gft2e.fit_params['tau'].value/1000)
        t2E_fits['gft2es_err'].append(gft2e.fit_params['tau'].stderr/1000)
    plt.figure(fig_num)
    plt.clf()
    plt.axis(xmin=-len(t2E_fits['gft2es'])*0.10, xmax=len(t2E_fits['gft2es'])*1.10, ymin= min(t2E_fits['gft2es'])*0.8, ymax=max(t2E_fits['gft2es'])*1.2)
    plt.errorbar(list(range(len(t2E_fits['gft2es']))),t2E_fits['gft2es'],t2E_fits['gft2es_err'],fmt='yv') # yellow color and v-shape markers
    plt.xlabel("Measurement iterations")
    plt.ylabel("GFT2Echo(us)")

def do_FT2echo_plot(qubit_info, ef_info, n_avg, delays, detune, t2E_fits, fig_num, laser_power = None):
    alz.set_naverages(n_avg)
    eft2e = do_EFT2echo(qubit_info, ef_info, delays, detune, laser_power = laser_power)
    if eft2e!=None:
        t2E_fits['eft2es'].append(eft2e.fit_params['tau'].value/1000)
        t2E_fits['eft2es_err'].append(eft2e.fit_params['tau'].stderr/1000)
    plt.figure(fig_num)
    plt.clf()
    plt.axis(xmin=-len(t2E_fits['eft2es'])*0.10, xmax=len(t2E_fits['eft2es'])*1.10, ymin= min(t2E_fits['eft2es'])*0.8, ymax=max(t2E_fits['eft2es'])*1.2)
    plt.errorbar(list(range(len(t2E_fits['eft2es']))),t2E_fits['eft2es'],t2E_fits['eft2es_err'],fmt='mv', label='EFT2echo') # magenta color and v-shape markers
    plt.errorbar(list(range(len(t2E_fits['gft2es']))),t2E_fits['gft2es'],t2E_fits['gft2es_err'],fmt='yv', label='GFT2echo') # yellow color and v-shape markers
    plt.xlabel("Measurement iterations")
    plt.ylabel("FT2Echo(us)")

    gft2e = do_GFT2echo(qubit_info, ef_info, delays, detune, laser_power = laser_power)
    if gft2e!=None:
        t2E_fits['gft2es'].append(gft2e.fit_params['tau'].value/1000)
        t2E_fits['gft2es_err'].append(gft2e.fit_params['tau'].stderr/1000)
    plt.figure(fig_num)
    plt.clf()
    plt.axis(xmin=-len(t2E_fits['gft2es'])*0.10, xmax=len(t2E_fits['gft2es'])*1.10, ymin= min(t2E_fits['eft2es'])*0.8, ymax=max(t2E_fits['gft2es'])*1.2)
    plt.errorbar(list(range(len(t2E_fits['eft2es']))),t2E_fits['eft2es'],t2E_fits['eft2es_err'],fmt='mv', label='EFT2echo') # magenta color and v-shape markers
    plt.errorbar(list(range(len(t2E_fits['gft2es']))),t2E_fits['gft2es'],t2E_fits['gft2es_err'],fmt='yv', label='GFT2echo') # yellow color and v-shape markers
    plt.xlabel("Measurement iterations")
    plt.ylabel("FT2Echo(us)")


def do_rabiup(qubit_info, ef_info, amps, QP_injection_delay=None, laser_power= None):
    if QP_injection_delay == None:
        rabiup = efrabi.EFRabi(qubit_info, ef_info, amps, laser_power = laser_power)
    else:
        rabiup = efrabi_QP.EFRabi_QP(qubit_info, ef_info, amps, QP_injection_delay, laser_power = laser_power)
        rabiup.data.set_attrs(QP_delay=QP_injection_delay)
    rabiup.data.set_attrs(field_current=field)
    rabiup.data.set_attrs(temperature=temp)
#    rabiup.data.set_attrs(laser_power=laser_power)
    rabiup.measure()
    plt.close()
    return rabiup

def do_rabinoup(qubit_info, ef_info, amps, force_period, QP_injection_delay=None, laser_power=None):
    if QP_injection_delay == None:
        rabinoup = efrabi.EFRabi(qubit_info, ef_info, amps, first_pi=False, force_period=force_period,laser_power = laser_power)
    else:
        rabinoup = efrabi_QP.EFRabi_QP(qubit_info, ef_info, amps, first_pi=False, force_period=force_period, QP_delay=QP_injection_delay)
        rabinoup.data.set_attrs(QP_delay=QP_injection_delay)
    rabinoup.data.set_attrs(field_current=field)
    rabinoup.data.set_attrs(temperature=temp)
#    rabinoup.data.set_attrs(laser_power=laser_power)
    rabinoup.measure()
    #population = 100*rabinoup.fit_params['amp'].value/(rabiup.fit_params['amp'].value+rabinoup.fit_params['amp'].value)
    plt.close()
    return rabinoup

def do_population_plot(qubit_info, ef_info, n_avg_rabiup, n_avg_rabinoup, amps, pops_fits, fig_num, QP_injection_delay=None, laser_power = None):
    alz.set_naverages(n_avg_rabiup)
    rabiup = do_rabiup(qubit_info, ef_info, amps, QP_injection_delay, laser_power = laser_power)
    if rabiup!=None:
        pops_fits['rabiupAmp'].append(abs(rabiup.fit_params['amp'].value))
        pops_fits['rabiupAmp_err'].append(rabiup.fit_params['amp'].stderr)
    plt.figure(fig_num).show()
    plt.clf()
    plt.subplot(211).axis(xmin=-len(pops_fits['rabiupAmp'])*0.10, xmax=len(pops_fits['rabiupAmp'])*1.10, ymin=min(pops_fits['rabiupAmp'])*0.7, ymax=max(pops_fits['rabiupAmp'])*1.3)
    plt.errorbar(list(range(len(pops_fits['rabiupAmp']))),pops_fits['rabiupAmp'],pops_fits['rabiupAmp_err'],fmt='b^')
    #plt.xlabel("Measurement iterations")
    plt.ylabel("Rabiup")

    alz.set_naverages(n_avg_rabinoup)
    rabinoup = do_rabinoup(qubit_info, ef_info, amps, force_period=rabiup.fit_params['period'].value, QP_injection_delay=QP_injection_delay, laser_power = laser_power)
    if rabinoup!=None:
        pops_fits['rabinoupAmp'].append(abs(rabinoup.fit_params['amp'].value))
        pops_fits['rabinoupAmp_err'].append(rabinoup.fit_params['amp'].stderr)
        #population.append(population)
    plt.figure(fig_num).show()
    plt.subplot(212).axis(xmin=-len(pops_fits['rabinoupAmp'])*0.10, xmax=len(pops_fits['rabinoupAmp'])*1.10, ymin=0.0, ymax=max(pops_fits['rabinoupAmp'])*2.0)
    plt.errorbar(list(range(len(pops_fits['rabinoupAmp']))),pops_fits['rabinoupAmp'],pops_fits['rabinoupAmp_err'],fmt='go')
    plt.xlabel("Measurement iterations")
    plt.ylabel("Rabinoup")

'''
def do_qubitSSBspec()
   from scripts.single_qubit import ssbspec
   qubitSSBspec = ssbspec.SSBSpec(qubit_info, np.linspace(-3e6, 3e6, 51), plot_seqs=False)
   qubitSSBspec.measure()
   return qubitSSBspec
'''
