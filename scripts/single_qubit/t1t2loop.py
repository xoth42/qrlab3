import mclient
import importlib
importlib.reload(mclient)
import numpy as np
import matplotlib as mpl
from .t1t2_plotting import do_T1_plot, do_T2_plot, do_T2echo_plot
from .t1t2_plotting import do_FT1_plot, do_GFT2_plot, do_EFT2_plot, do_EFT2echo_plot, do_GFT2echo_plot, do_FT2echo_plot
from .t1t2_plotting import do_QPdecay_plot, do_population_plot, smart_T1_delays, calibrate_IQ
#from automation_helper import auto_set_fg_freq, estimate_T1

################################################################################################################################################
mpl.rcParams['figure.figsize']=[5,3.5]
mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']

# Load old settings.
if 0:
    toload = ['AWG1']
    mclient.load_settings_from_file(r'c:\_data\settings\20131119\094145.set', toload)    # Last time-Rabi callibration

awg1 = mclient.instruments['AWG1']
fg = mclient.instruments['funcgen']
alz = mclient.instruments['alazar']
ag1 = mclient.instruments['ag1']
LO = mclient.instruments['brick_LO']
ag3 = mclient.instruments['ag3']
ag2 = mclient.instruments['ag2']
brick1 = mclient.instruments['brick1']
brick2 = mclient.instruments['brick2']


qDblCoax = mclient.get_qubit_info('qubit1ge')
eDblCoax = mclient.get_qubit_info('qubit1ef')
#qDblCoax2 = mclient.get_qubit_info('qubit2ge')
#eDblCoax2 = mclient.get_qubit_info('qubit2ef')
#qAG13_4 = mclient.get_qubit_info('qAG13#4')
#eAG13_4= mclient.get_qubit_info('qAG13#4')

readout_info = mclient.instruments['readout']

################################################################################################################################################

#I15_1_t1s = {'t1s':[], 't1s_err':[], 'ofs':[], 'amps':[], 'qpt1s':[],'qpt1s_err':[], 'qpofs':[], 'qpofs_err':[],'t1s_QP':[], 't1s_QP_err':[]}
#I15_1_t2s = {'t2s':[], 't2s_err':[], 't2freqs':[], 't2freqs_err':[], 'amps':[], 'amps_err':[], 't22s':[], 't22s_err':[], 't22freqs':[], 't22freqs_err':[], 'amp2s':[], 'amp2s_err':[],}
#I15_1_t2Es = {'t2es':[], 't2es_err':[]}
#I15_1_ft1s = {'ft1s':[], 'ft1s_err':[], 'ofs':[], 'amps':[]}
#I15_1_pops = {'rabiupAmp':[], 'rabiupAmp_err':[], 'rabinoupAmp':[], 'rabinoupAmp_err':[]}

DblCoax_t1s = {'t1s':[], 't1s_err':[], 'ofs':[], 'amps':[], 'qpt1s':[],'qpt1s_err':[], 'qpofs':[], 'qpofs_err':[],'t1s_QP':[], 't1s_QP_err':[]}
DblCoax_t2s = {'t2s':[], 't2s_err':[], 't2freqs':[], 't2freqs_err':[], 'amps':[], 'amps_err':[], 't22s':[], 't22s_err':[], 't22freqs':[], 't22freqs_err':[], 'amp2s':[], 'amp2s_err':[],}
DblCoax_t2Es = {'t2es':[], 't2es_err':[], 'eft2es':[], 'eft2es_err':[], 'gft2es':[], 'gft2es_err':[]}
DblCoax_ft1s = {'ft1s':[], 'ft1s_err':[], 'ofs':[], 'amps':[]}
DblCoax_ft2s = {'eft2s':[], 'eft2s_err':[], 'eft2freqs':[], 'eft2freqs_err':[], 'eft2amps':[], 'eft2amps_err':[], 'eft22s':[], 'eft22s_err':[], 'eft22freqs':[], 'eft22freqs_err':[], 'eft2amp2s':[], 'eft2amp2s_err':[], 'gft2s':[], 'gft2s_err':[], 'gft2freqs':[], 'gft2freqs_err':[], 'gft2amps':[], 'gft2amps_err':[], 'gft22s':[], 'gft22s_err':[], 'gft22freqs':[], 'gft22freqs_err':[], 'gft2amp2s':[], 'gft2amp2s_err':[],}
DblCoax_pops = {'rabiupAmp':[], 'rabiupAmp_err':[], 'rabinoupAmp':[], 'rabinoupAmp_err':[]}

################################################################################################################################################

def auto_set_fg_freq(seq_len, max_freq=10000):
    fg_freqs = [20000, 16000, 12500, 10000, 8000, 6250, 5000, 4000, 3200, 2500, 2000, 1600, 1250, 1000, 800, 625, 500, 400, 320, 250, 200, 160, 125, 100]
    for freq in fg_freqs:
        if (freq <= max_freq) and (seq_len < 1.0e9/freq):
            fg.set_frequency(freq)
            return freq
    print("Warning: auto_set_fg_frequency failed!")
    return

def estimate_T1(QP_delay, T1_int=90e3, tau_QP=1.5e6, half_decay_point=1e6, eff_T1_delay=500.0):
    T1_QPref = 1/(np.log(2)/eff_T1_delay-1/T1_int)      # T1 at half decay point = effective readout delay/ln(2), excluding intrinsic part giving the T1 due to quasiparticles
    return 1/(1/T1_int+1/T1_QPref*np.exp(-(QP_delay-half_decay_point)/tau_QP))

def switch_to_qubit(qubit_info, HP_readout=True):
#
    if qubit_info == qI15_7:
        brick2.set_frequency(6048.685e6)
        ag1.set_frequency(9067.250e6)
        LO.set_frequency(9117.250e6)
        ag3.set_frequency(9051.080e6)
        ag1.set_power(-30)
#        ag1.set_power(-30)
#        ag3.set_power(25)
        awg1.do_set_amplitude(3.0, 3)
        awg1.do_set_amplitude(3.420, 4)
#        awg1.do_set_offset(-0.024, 1)
#        awg1.do_set_offset(0.151, 2)
        awg1.do_set_offset(-0.012, 3)
        awg1.do_set_offset(0.028, 4)
        readout_info.set_pulse_len(1000)
        alz.set_nsamples(6400)
        readout_info.set_IQe(0.0841790505706+0.404431017432j)
        readout_info.set_IQg(-1.70172669613+2.83615344763j)
        readout_info.set_rotype('Dispersive')
        filename = 'c:/_data/150202 Cooldown/I15#3.hdf5'
        mclient.datafile = mclient.datasrv.get_file(filename)
#
    if qubit_info == qI15_8:
        brick2.set_frequency(6364.490e6)
        ag1.set_frequency(9067.250e6)
        LO.set_frequency(9117.250e6)
        ag3.set_frequency(9051.080e6)
        ag1.set_power(-30)
#        ag3.set_power(25)
        awg1.do_set_amplitude(3.0, 3)
        awg1.do_set_amplitude(3.357, 4)
#        awg1.do_set_offset(-0.024, 1)
#        awg1.do_set_offset(0.151, 2)
        awg1.do_set_offset(-0.005, 3)
        awg1.do_set_offset(0.037, 4)
        readout_info.set_pulse_len(1000)
        alz.set_nsamples(6400)
        readout_info.set_IQe(0.0841790505706+0.404431017432j)
        readout_info.set_IQg(-1.70172669613+2.83615344763j)
        readout_info.set_rotype('Dispersive')
        filename = 'c:/_data/150202 Cooldown/I15#4.hdf5'
        mclient.datafile = mclient.datasrv.get_file(filename)


################################################################################################################################################
'''Dblcoax'''
qubit = [qDblCoax, eDblCoax]
#switch_to_qubit(qubit[0])
rep_rates = [125, 80]

for i in range(100):
    if 1:
#    for j in range(3):
        for rep_rate in rep_rates:
            fg.set_frequency(rep_rate)
#            brick2.set_rf_on(True)
            do_T1_plot(qubit[0], 150, np.concatenate((np.linspace(0, 60e3, 41), np.linspace(61e3, 350e3, 61))),DblCoax_t1s, 100)
            do_T2_plot(qubit[0], 150, np.linspace(0, 25e3, 101), 600e3, DblCoax_t2s, 101, double_freq=False)
            do_T2echo_plot(qubit[0], 150, np.linspace(0.5e3, 60e3, 101), 200e3, DblCoax_t2Es, 102)
            do_FT1_plot(qubit[0], qubit[1], 300, np.concatenate((np.linspace(0, 40e3, 51), np.linspace(41e3, 160e3, 51))), DblCoax_ft1s, 103)
            do_EFT2_plot(qubit[0], qubit[1], 120, np.linspace(0, 25e3, 81), 500e3, DblCoax_ft2s, 104, double_freq=False)
            do_GFT2_plot(qubit[0], qubit[1], 120, np.linspace(0, 20e3, 81), 600e3, DblCoax_ft2s, 105, double_freq=False)
            do_FT2echo_plot(qubit[0], qubit[1], 120, np.linspace(0.5e3, 30e3, 81), 400e3, DblCoax_t2Es, 106)
            do_population_plot(qubit[0], qubit[1], 120, 1000, np.linspace(-0.8, 0.8, 61), DblCoax_pops, 107)

#        fg.set_frequency(2000)
#        from pulseseq import sequencer
#        from scripts.single_qubit import rabi
#        seq = sequencer.Join([sequencer.Trigger(250), sequencer.Repeat(qubit[0].rotate(np.pi, 0), 20)])
#        tr = rabi.Rabi(qubit[0], np.linspace(-0.6, 0.6, 81), plot_seqs=False, update=False, seq=seq, selective=False, singleshotbin=True)#, fix_period=0.00924)
#        tr.measure()

################################################################################################################################################
'''Dblcoax2
qubit = [qDblCoax2, eDblCoax2]
#switch_to_qubit(qubit[0])
rep_rates = [2000, 1000, 500]

for i in range(100):
    if 1:
#    for j in range(3):
        for rep_rate in rep_rates:
            fg.set_frequency(rep_rate)
            do_T1_plot(qubit[0], 2000, np.concatenate((np.linspace(0, 80e3, 41), np.linspace(82e3, 475e3, 61))),DblCoax_t1s, 100)
            do_T2_plot(qubit[0], 2000, np.linspace(0, 100e3, 101), 120e3, DblCoax_t2s, 101, double_freq=False)
            do_T2echo_plot(qubit[0], 2000, np.linspace(0.2e3, 120e3, 101), 100e3, DblCoax_t2Es, 102)
            do_FT1_plot(qubit[0], qubit[1], 3000, np.concatenate((np.linspace(0, 60e3, 51), np.linspace(62e3, 200e3, 51))), DblCoax_ft1s, 103)
            do_EFT2_plot(qubit[0], qubit[1], 2000, np.linspace(0, 40e3, 101), 300e3, DblCoax_ft2s, 104, double_freq=False)
            do_GFT2_plot(qubit[0], qubit[1], 2000, np.linspace(0, 40e3, 101), 300e3, DblCoax_ft2s, 105, double_freq=False)
            do_FT2echo_plot(qubit[0], qubit[1], 2000, np.linspace(0.5e3, 50e3, 101), 300e3, DblCoax_t2Es, 106)
            do_population_plot(qubit[0], qubit[1], 1500, 15000, np.linspace(-1,1,81), DblCoax_pops, 107)
'''
################################################################################################################################################
'''
qubit = [qI15_4, eI15_4]
#qubit = [qI15_3, eI15_3]
switch_to_qubit(qubit[0])

rep_rates = [4000, 1000, 4000, 1000]
probe_points = [0.5]
injection_lengths = [360e3,600e3]
inj_power =[20]
eff_T1_delay = 500
meas_per_QPinj = 4
meas_per_reptime = 50
T1_int = 16.0e3
QPT1 = 0.3e6
half_decay_point = 0.3e6

T1_delays = smart_T1_delays(T1_int=T1_int, QPT1=QPT1, half_decay_point=half_decay_point, eff_T1_delay=eff_T1_delay, probe_point=0.5, meas_per_QPinj=meas_per_QPinj, meas_per_reptime=meas_per_reptime)

#set to high power readout:
if 0:
    ag1.set_frequency(9022.94e6)
    LO.set_frequency(9072.94e6)
    ag1.set_power(4.5)
#    ag3.set_rf_on(True)
    readout_info.set_pulse_len(1000)
    alz.set_ch2_range('1V')
    readout_info.set_rotype('High-power')


for i in range(20):

    if 0:
        for rep_rate in rep_rates:
            fg.set_frequency(rep_rate)
#        for j in range (5):
            do_T1_plot(qubit[0], 1500, np.concatenate((np.linspace(0, 40e3, 41), np.linspace(41e3, 120e3, 80))),I15_3_t1s, 200)
            do_T2_plot(qubit[0], 1500, np.linspace(0, 30e3, 101), 500e3, I15_3_t2s, 201)
            do_T2echo_plot(qubit[0], 1500, np.linspace(0.3e3, 50e3, 101), 400e3,I15_3_t2Es, 202)
#            do_FT1_plot(qubit[0], qubit[1], 1000, np.linspace(0, 50000, 101), FC14a_ft1s, 303)

        if 0:
            do_population_plot(qubit[0], qubit[1], 500, 30000, np.linspace(0,0.5,61),I15_3_pops, 204)

    if 0:
#        ag3.set_power(25)
        ag3.set_rf_on(True)
        fg.set_frequency(1000)
#                for power in inj_power:
        for length in injection_lengths:
            ve, vg = calibrate_IQ(qubit[0], 50000)
            ag3.set_power(20)
            inj_len = length
            for j in range (2):
                qpd=do_QPdecay_plot(qubit[0], 2500, T1_delays, I15_3_t1s, 306, meas_per_reptime = meas_per_reptime, meas_per_QPinj=None, fit_start=5, fit_end=None, vg=vg, ve=ve+0.1, eff_T1_delay=eff_T1_delay, inj_len=inj_len)
                T1_delays = (T1_delays -np.log(0.5)*1000.0/qpd.invT1 - eff_T1_delay)/2 # Update the new T1_delay array to be the average of the existing one and the newly measured values
                for j, delay in enumerate(T1_delays):
                    if delay < 0:
                        T1_delays[j]=0.0

#set to high power readout:
    if 1:
        ag1.set_frequency(9051.080e6)
        LO.set_frequency(9101.080e6)
        ag1.set_power(8.0)
        ag3.set_rf_on(True)
        readout_info.set_pulse_len(1000)
        alz.set_ch2_range('1V')
        readout_info.set_rotype('High-power')

    if 1:
#        QP_delays = np.linspace(1.1e6, 5.0e6, 11)
        QP_delays = np.concatenate((np.linspace(0.1e6, 0.81e6, 17), np.linspace(0.81e6, 3.50e6, 17)))
#        QP_delays =  [0.1e6]
#        for power in injection_power:
#            ag3.set_power(power)
        for length in injection_lengths:
            QP_injection_length = length
#            QP_injection_length = 360e3
            for QP_delay in QP_delays:
                auto_set_fg_freq(QP_delay + QP_injection_length + 100e3, max_freq=1000)
                T1guess = estimate_T1(QP_delay, T1_int, QPT1, half_decay_point, eff_T1_delay=eff_T1_delay)
#                if power <10:
#                    T1guess = 1.5*estimate_T1(QP_delay, T1_int, QPT1, half_decay_point/5.0, eff_T1_delay=eff_T1_delay)
    #                if power <11:
    #                    T1guess = 2.0*estimate_T1(QP_delay, T1_int, QPT1, half_decay_point/3.0, eff_T1_delay=eff_T1_delay)
                if QP_delay < 0.4e6:
                    avg =  900
                    avg2 = 1000
                    T1end = T1guess*5
                elif QP_delay < 0.2e6:
                    avg = 600
                    avg2 = 600
                    T1end = T1guess*8
                else:
                    avg = 500
                    avg2 = 2000
                    T1end = T1guess*8

                do_T1_plot(qubit[0], avg, np.linspace(0, T1end, 101), I15_3_t1s, 307, QP_injection_delay=QP_delay, QP_injection_length = QP_injection_length)
'''
################################################################################################################################################
'''
#qubit = [qI15_5, eI15_5]
qubit = [qI15_6, eI15_6]
switch_to_qubit(qubit[0])

probe_points = [0.5]
injection_lengths = [360e3, 600e3]
inj_power =[25]

eff_T1_delay = 500.0
meas_per_QPinj = 4
meas_per_reptime = 50
T1_int = 40e3
QPT1 = 0.4e6
half_decay_point = 0.3e6

T1_delays = smart_T1_delays(T1_int=T1_int, QPT1=QPT1, half_decay_point=half_decay_point, eff_T1_delay=eff_T1_delay, probe_point=0.5, meas_per_QPinj=meas_per_QPinj, meas_per_reptime=meas_per_reptime)

#set to high power readout:
if 0:
    ag1.set_frequency(9060.94e6)
    LO.set_frequency(9110.94e6)
    ag1.set_power(2.0)
    readout_info.set_pulse_len(1000)
    alz.set_ch2_range('1V')
    readout_info.set_rotype('High-power')

for i in range(100):
#
#    fg.set_frequency(1000)

    if 0:
#        for  j in range(5):
        for reprate in [4000, 1000, 4000, 1000]:
            fg.set_frequency(reprate)
            do_T1_plot(qubit[0], 1000, np.concatenate((np.linspace(0, 40e3, 50), np.linspace(41e3, 180e3, 45))), I15_5_t1s, 400)
            do_T2_plot(qubit[0], 1000, np.linspace(0, 25e3, 101), 800e3, I15_5_t2s, 401)
            do_T2echo_plot(qubit[0], 1000, np.linspace(0.3e3, 40e3, 101), 400e3, I15_5_t2Es, 402)
#            do_FT1_plot(qubit[0], qubit[1], 1000, np.linspace(0, 60000, 101), AG13_3_ft1s, 203)
        if 0:
            do_population_plot(qubit[0], qubit[1], 500, 30000, np.linspace(0,0.5,61), I15_5_pops, 404)


    if 1:
#        ve, vg = calibrate_IQ(qubit[0], 50000)
#        for power in inj_power:
#            ag3.set_power(power)
#            for j in range (3):
        for length in injection_lengths:
            inj_len = length
            ve, vg = calibrate_IQ(qubit[0], 50000)
            for j in range(2):
                qpd=do_QPdecay_plot(qubit[0], 3000, T1_delays,I15_5_t1s, 406, meas_per_reptime = meas_per_reptime, meas_per_QPinj=None, fit_start=5, fit_end=None, vg=vg, ve=ve, eff_T1_delay=eff_T1_delay, inj_len=inj_len)
                T1_delays = (T1_delays -np.log(0.5)*1000.0/qpd.invT1 - eff_T1_delay)/2 # Update the new T1_delay array to be the average of the existing one and the newly measured values
                for j, delay in enumerate(T1_delays):
                    if delay < 0:
                        T1_delays[j]=0.0


    if 0:
    #        QP_delays = np.concatenate((np.linspace(0.1e6, 1.3e6, 13), np.linspace(1.5e6, 3.5e6, 9)))
        QP_delays = np.concatenate((np.linspace(0.15e6, 0.28e6, 21), np.linspace(0.3e6, 1.3e6, 21), np.linspace(1.5e6, 5.5e6, 11)))
        for power in inj_power:
            ag3.set_power(power)
    #        for length in injection_lengths:
    #            QP_injection_length = length
            for QP_delay in QP_delays:
                auto_set_fg_freq(QP_delay+500e3, max_freq=1000)
                T1guess = estimate_T1(QP_delay, T1_int, QPT1, half_decay_point, eff_T1_delay=eff_T1_delay)
    #                if length <360e3:
    #                    T1guess = 1.5*estimate_T1(QP_delay, T1_int, QPT1, half_decay_point/5.0, eff_T1_delay=eff_T1_delay)
    #                if power <11:
    #                    T1guess = 2.0*estimate_T1(QP_delay, T1_int, QPT1, half_decay_point/3.0, eff_T1_delay=eff_T1_delay)
                if QP_delay < 0.2e6:
                    avg =  2000
                    avg2 = 2000
                    T1end = T1guess*3
                elif QP_delay < 0.8e6:
                    avg = 1000
                    avg2 = 1500
                    T1end = T1guess*5
                else:
                    avg = 600
                    avg2 = 600
                    T1end = T1guess*15

                do_T1_plot(qubit[0], avg, np.linspace(0, T1end, 101), FC14_2_t1s, 407, QP_injection_delay=QP_delay, QP_injection_length = 360e3)
#            do_T2_plot(qubit[0], avg, np.linspace(0, T1end, 81), 5e6, AG13_8_t2s, 207, double_freq=False, QP_injection_delay=QP_delay)
'''
#################################################################################################################################################
#FP14#1#2
'''
probe_points = [0.5]#[0.25, 0.5, 0.75]
T1_int= 30e3
half_decay_point=0.4e6
QPT1= 0.4e6

meas_per_QPinj = 4
meas_per_reptime = 50
eff_T1_delay = 500.0
#T1_delays = smart_T1_delays(T1_int=T1_int, QPT1=QPT1, half_decay_point=half_decay_point, eff_T1_delay=eff_T1_delay, probe_point=0.5, meas_per_QPinj=meas_per_QPinj, meas_per_reptime=meas_per_reptime)

#qubit = [qFP14_1, eFP14_1]
qubit = [qFP14_2, eFP14_2]
#switch_to_qubit(qubit[0])
injection_lengths = [360e3]#[600e3, 360e3, 100e3, 60e3, 10e3]
#ves=[]
#vgs=[]
rep_rates = [5000, 2000, 1000, 500, 200, 100]

if 0:
    ag1.set_frequency(9217.475e6)
    LO.set_frequency(9267.475e6)
    ag1.set_power(7)
    ag3.set_power(20)
    readout_info.set_pulse_len(1000)
    alz.set_ch2_range('1V')
    readout_info.set_rotype('High-power')

for i in range(100):

    if 1:
        for rep in rep_rates:
#        for j in range(1):
            fg.set_frequency(rep)
            do_T1_plot(qubit[0], 800, np.concatenate((np.linspace(0, 100e3, 81), np.linspace(100e3, 250e3, 60))), FP14_1_t1s, 400)
            do_T2_plot(qubit[0], 1000, np.linspace(0, 30e3, 101), 300e3,FP14_1_t2s, 401, double_freq=False)
            do_T2echo_plot(qubit[0], 1000, np.linspace(0, 50e3, 101), 100e3, FP14_1_t2Es, 402)
#            do_FT1_plot(qubit[0], qubit[1], 1500, np.linspace(0, 200e3, 101), SP_1_ft1s, 403)
        if 0:
            fg.set_frequency(1000)
            do_population_plot(qubit[0], qubit[1], 400, 4000, np.linspace(0,1,61), FP14_1_pops, 404)

#
    if 0:
        ve, vg = calibrate_IQ(qubit[0], 50000)
        for j in range (3):
            inj_len = 360e3
            qpd = do_QPdecay_plot(qubit[0], 6000, T1_delays, FP14_1_t1s, 406, meas_per_reptime=meas_per_reptime, meas_per_QPinj=None, fit_start=2, fit_end=None, vg=vg, ve=ve, eff_T1_delay=eff_T1_delay,inj_len=inj_len)
            T1_delays = (T1_delays -np.log(0.5)*1000.0/qpd.invT1 - eff_T1_delay)/2 # Update the new T1_delay array to be the average of the existing one and the newly measured values
            for k, delay in enumerate(T1_delays):
                if delay < 0:
                    T1_delays[k]=0.0


    if 0:
        ag1.set_frequency(9217.475e6)
        LO.set_frequency(9267.475e6)
        ag1.set_power(7)
        ag3.set_power(25)
        readout_info.set_pulse_len(1000)
        readout_info.set_IQe(0)
        readout_info.set_IQg(100j)
        alz.set_ch2_range('1V')
        readout_info.set_rotype('High-power')


        QP_delays = np.concatenate((np.linspace(0.05e6, 0.22e6, 21), np.linspace(0.25e6, 1.15e6, 11), np.linspace(1.25e6, 5e6, 16)))
#        QP_delays =[4.5e6, 4.75e6, 5e6]
        for length in injection_lengths:
            QP_injection_length = length
            for QP_delay in QP_delays:
                auto_set_fg_freq(QP_delay+100e3+QP_injection_length, max_freq=1250)
                T1guess = estimate_T1(QP_delay, T1_int, QPT1, half_decay_point, eff_T1_delay=eff_T1_delay)
                if length <100e3:
                    T1guess = 1.5*estimate_T1(QP_delay, T1_int, QPT1, half_decay_point/2.0, eff_T1_delay=eff_T1_delay)
                if QP_delay < 0.2e6:
                    avg =  1000
                    avg2 = 4000
                    T1end = T1guess*80
                elif QP_delay < 0.5e6:
                    avg = 600
                    avg2 = 2500
                    T1end = T1guess*100
                else:
                    avg = 300
                    avg2 = 800
                    T1end = T1guess*100
    #            f2 = 20*1e9/T1end
                do_T1_plot(qubit[0], avg, np.linspace(0, T1end, 101), FP14_1_t1s, 407, QP_injection_delay = QP_delay, QP_injection_length=length)
    #            do_T2_plot(qubit[0], avg2, np.linspace(0, min(T1end*0.4, 50e3), 101), max(f2, 400e3), SP_1_t2s, 408, double_freq=False, QP_injection_delay=QP_delay, QP_injection_length=10e3)

'''
#################################################################################################################################################
'''
qubit = [qubit_AG13_4, ef_AG13_4]
switch_to_qubit(qubit[0])

if 0:
    do_T1_plot(qubit[0], 2500, np.concatenate((np.linspace(0, 160e3, 81), np.linspace(160e3, 300e3, 61))), AG13_4t1s, 300)
    do_T2_plot(qubit[0], 2500, np.linspace(0, 12000, 101), 800e3, AG13_4_t2s, 301, double_freq=False, QP_injection_delay=None)
    do_T2echo_plot(qubit[0], 2500, np.linspace(0, 30000, 81), 400e3, AG13_4_t2Es, 302)
    do_FT1_plot(qubit[0], qubit[1], 4000, np.linspace(0, 100000, 81), AG13_4_ft1s, 303)
    if i%20==19:
         do_population_plot(qubit[0], qubit[1], 3000, 60000, np.linspace(0,1,61), AG13_4_pops, 304)


if 0:
    fg.set_frequency(2500)
    ve, vg = calibrate_IQ(qubit[0], 50000)
    ves.append(ve)
    vgs.append(vg)
    qpd=do_QPdecay_plot(qubit[0], 6000, T1_delays_10, AG13_4_t1s, 306, meas_per_reptime=meas_per_reptime, meas_per_QPinj=None, fit_start=15, fit_end=None, vg=0.09, ve=2.63, eff_T1_delay=1600.0)
    T1_delays_10 = (T1_delays_10 -np.log(0.5)*1000.0/qpd.invT1 - eff_T1_delay)/2 # Update the new T1_delay array to be the average of the existing one and the newly measured values
    for k, delay in enumerate(T1_delays_10):
        if delay < 0:
            T1_delays_10[k]=0.0

#        qpd=do_QPdecay_plot(qubit[0], 2500, T1_delays, AG13_8_t1s, 206, meas_per_reptime=2, meas_per_QPinj=None, fit_start=4, fit_end=None, vg=0.0, ve=6.5, eff_T1_delay=340.0)

if 0:
    ag1.set_frequency(9.05925e9)
    ag2.set_frequency(9.10925e9)
    ag1.set_power(12)
    readout_info.set_pulse_len(1000)
    alz.set_ch2_range('1V')
    readout_info.set_rotype('High-power')

    QP_delays = np.concatenate((np.linspace(0.2e6, 1.1e6, 10), np.linspace(1.2e6, 4.0e6, 15)))
    for QP_delay in QP_delays:
        auto_set_fg_freq(QP_delay+200e3, max_freq=1000)
        T1guess = estimate_T1(QP_delay, T1_int_10, QPT1_10, half_decay_point_10, eff_T1_delay=eff_T1_delay)
        if QP_delay < 1e6:
            avg = 1000
        else:
            avg = 400
        do_T1_plot(qubit[0], avg, np.linspace(0, T1guess*6, 81), AG13_10_t1s, 307, QP_injection_delay=QP_delay)
        do_T2_plot(qubit[0], avg, np.linspace(0, T1guess, 81), 5e6, AG13_10_t2s, 308, double_freq=False, QP_injection_delay=QP_delay)
'''