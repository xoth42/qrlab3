import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import matplotlib.pyplot as plt
import copy
import mclient
import lmfit

def fit_timerabi(params, x, data):
    decay = np.exp(-x / params['decay'].value)
    est = params['ofs'].value - params['amp'].value * np.cos(2*np.pi*x / params['period'].value) * decay
    return data  - est

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.areas

    fig.axes[0].plot(xs, ys, 'ks', ms=3)

    amp0 = (np.max(ys) - np.min(ys)) / 2
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    period0 = 1 / np.abs(fftfs[np.argmax(fftys)])

    params = lmfit.Parameters()
    params.add('ofs', value=np.average(ys))
    params.add('amp', value=amp0)
    params.add('period', value=period0, min=0)
    params.add('decay', value=20000, min=0)
    global result
    result = lmfit.minimize(fit_timerabi, params, args=(xs, ys))
    lmfit.report_fit(params)

    if params['period'] != 0:
        pi_area = params['period'] / 2
    else:
        pi_area = 0

    txt = 'Fit, pi area = %.03f' % (pi_area, )
    print txt
    fig.axes[0].plot(xs, -fit_timerabi(params, xs, 0), label=txt)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Pulse area')
    fig.axes[0].legend(loc=0)

    fig.axes[1].plot(xs, fit_timerabi(params, xs, ys), marker='s')
    fig.canvas.draw()
    return pi_area

class TimeRabi(Measurement1D):

    def __init__(self, qubit_info, areas, update=False, seq=None, extra_info=None, **kwargs):
        self.qubit_info = qubit_info
        self.areas = areas
        self.xs = areas
        self.update_ins = update
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.extra_info = extra_info

        super(TimeRabi, self).__init__(len(areas), **kwargs)
        self.data.create_dataset('areas', data=areas)

    def generate(self):
        s = Sequence()

        for i, pulse_area in enumerate(self.areas):
            r = copy.deepcopy(self.qubit_info.rotate)
            r.set_pi(pulse_area)
            rpi = r(np.pi, 0)
            s.append(Join([
                self.seq,
                rpi])
            )
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))

        s = Sequencer(s)
        seqs = s.render()
        if self.qubit_info.ssb:
            self.qubit_info.ssb.modulate(seqs)
        if self.extra_info and self.extra_info.ssb:
            self.extra_info.ssb.modulate(seqs)
#        s.plot_seqs(seqs)

        self.seqs = seqs
        return seqs

    def analyze(self, data=None, fig=None):
        pi_area = analysis(self, data=data, fig=fig)
        if self.update_ins:
            print 'Setting qubit pi-rotation area to %.03f' % pi_area
            mclient.instruments[self.qubit_info.insname].set_pi_area(pi_area)
        return pi_area
