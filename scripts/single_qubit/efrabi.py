import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import matplotlib.pyplot as plt
import copy
import mclient
import lmfit

def fit_amprabi(params, x, data):  # 5/19 corrected the fit function.  Was using a timerabi function, how?
    est = params['ofs'].value - params['amp'].value * np.cos(2*np.pi*x / params['period'].value + params['phase'].value)
    return data  - est

def analysis(meas, data=None, fig=None, period=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.amps

    fig.axes[0].plot(xs, ys, 'ks', ms=3)

    amp0 = (np.min(ys) - np.max(ys)) / 2
#    if ys[0]>np.average(ys):
#        amp0 = -amp0
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    period0 = 1 / np.abs(fftfs[np.argmax(fftys)])

    params = lmfit.Parameters()
    params.add('ofs', value=np.average(ys))
    params.add('amp', value=amp0)
    params.add('phase', value=0, vary=False)
    if period is not None:
        params.add('period', value=period, min=0, vary=False)
    else:
        params.add('period', value=period0, min=0)
    result = lmfit.minimize(fit_amprabi, params, args=(xs, ys))
    lmfit.report_fit(result.params)

    txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.05f' % (result.params['amp'].value, result.params['amp'].stderr, result.params['period'].value, result.params['period'].stderr, result.params['period'].value/2 )
    fig.axes[0].plot(xs, -fit_amprabi(result.params, xs, 0), label=txt)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Pulse area')
    fig.axes[0].legend(loc=0)

    fig.axes[1].plot(xs, fit_amprabi(result.params, xs, ys), marker='s')
    fig.canvas.draw()
    return result.params

class EFRabi(Measurement1D):

    def __init__(self, ge_info, ef_info, amps, first_pi=True, second_pi=True, selective=False,
                 update=False, seq=None, repeat_pulse=1, laser_power = None,
                 force_period=None, postseq = None,
                 **kwargs):
        self.ge_info = ge_info
        self.ef_info = ef_info
        self.amps = amps
        self.first_pi = first_pi
        self.second_pi = second_pi
        self.xs = amps
        self.update_ins = update
        self.force_period = force_period

        self.selective = selective
        self.repeat_pulse = repeat_pulse
        self.laser_power = laser_power
        self.postseq = postseq
        if seq is None:
            seq = Trigger(250)
        self.seq = seq

        super(EFRabi, self).__init__(len(amps), infos=(ge_info, ef_info), **kwargs)
        self.data.create_dataset('areas', data=amps)
        if laser_power:
            self.data.set_attrs(laser_power =self.laser_power)

    def generate(self):
        s = Sequence()

        for i, amp in enumerate(self.amps):
            r = self.ge_info.rotate
            if self.selective==1:
                r_ef = self.ef_info.rotate_selective
            elif self.selective==0.5:
                r_ef = self.ef_info.rotate_quasilective
            else:
                r_ef = self.ef_info.rotate
            add = self.seq
            if self.first_pi:
                add = Join([add, r(np.pi, 0), Delay(5)])
            add = Join([add, Repeat(r_ef(0, 0, amp = amp), self.repeat_pulse), Delay(5)])
            if self.second_pi:
                add = Join([add, r(np.pi, 0), Delay(5)]) # What? Why was this Delay 250? 5/28/2019
#            marker_switch = Constant(, 1, chan=self.)
            s.append(add)
            if self.postseq:
                s.append(self.postseq)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000))

        s = self.get_sequencer(s)
        seqs = s.render()
        self.seqs = seqs
        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig, period=self.force_period)
        pi_amp = self.fit_params['period'].value / 2
        if self.update_ins:
            print 'Setting qubit pi-rotation area to %.03f' % pi_amp
            mclient.instruments[self.ef_info.insname].set_pi_amp(pi_amp)
        return pi_amp
