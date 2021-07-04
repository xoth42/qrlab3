from . import mclient
import numpy as np

fg = mclient.instruments['funcgen']
alz = mclient.instruments['alazar']
brick1 = mclient.instruments['brick1']
brick2 = mclient.instruments['brick2']
ag3 = mclient.instruments['ag3']

################################################################################################################################################

def auto_set_fg_freq(seq_len, max_freq=10000):
    fg_freqs = [20000, 12500, 10000, 8000, 5000, 4000, 2500, 2000, 1250, 1000, 800, 500, 400, 250, 200, 125, 100]
    for freq in fg_freqs:
        if (freq <= max_freq) and (seq_len < 1.0/freq):
            fg.set_frequency(freq)
            return freq
    print("Warning: auto_set_fg_frequency failed!")
    return

def estimate_T1(QP_delays, T1_int=90e3, tau_QP=1.5e6, half_decay_point=1e6, eff_T1_delay=500.0):
    T1_QPref = 1/(np.log(2)/eff_T1_delay-1/T1_int)      # T1 at half decay point = effective readout delay/ln(2), excluding intrinsic part giving the T1 due to quasiparticles
    return 1/(1/T1_int+1/T1_QPref*np.exp(-(QP_delays-half_decay_point)/tau_QP))


def smart_T1_delays(T1_int=90e3, QPT1=1.5e6, half_decay_point=1e6, eff_T1_delay=800.0, probe_point=0.5, meas_per_QPinj=30, meas_per_reptime=5):
    """
    T1_int = 90e3                  # Intrinsic T1 of the qubit
    QPT1 = 1.5e6                    # Guess the T1 of the quasiparticles
    half_decay_point = 1e6        # The QP_delay time that would make qubit relax halfway to ground state even with T1_delay=0, i.e. relax during readout pulse
    eff_T1_delay = 800.0            # The effective T1_delay due to the finite length of the readout pulse
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

    QP_times = np.linspace(step_time, n_points*step_time, n_points)
    T1_est = 1/(1/T1_int+1/T1_QPref*np.exp(-(QP_times-half_decay_point)/QPT1))
    T1_delays = -np.log(probe_point)*T1_est-eff_T1_delay
    for j, delay in enumerate(T1_delays):
        if delay < 0:
            T1_delays[j]=0.0
    return T1_delays
