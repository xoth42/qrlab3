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
    xs = meas.phases

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
    params.add('phase', value=0)
    params.add('period', value=np.pi*2, vary=False)
    result = lmfit.minimize(fit_amprabi, params, args=(xs, ys))
    lmfit.report_fit(result.params)

    txt = 'Amp = %.03f +- %.03e\nPhase = %.03f +- %.03e\nPi amp = %.05f' % (result.params['amp'].value, result.params['amp'].stderr, result.params['phase'].value, result.params['period'].stderr, result.params['period'].value/2 )
    fig.axes[0].plot(xs, -fit_amprabi(result.params, xs, 0), label=txt)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Pulse area')
    fig.axes[0].legend(loc=0)

    fig.axes[1].plot(xs, fit_amprabi(result.params, xs, ys), marker='s')
    fig.canvas.draw()
    return result.params

class geophasecal(Measurement1D):

    def __init__(self, control_info, zx90_info, gate_info1, phases, seq=None, repeat_pulse=1, delay=0, postseq = None,
                 **kwargs):
        self.control_info = control_info
        self.zx90_info = zx90_info
        self.gate_info1 = gate_info1
        self.phases = phases
        self.delay = delay

        self.xs = phases
        self.repeat_pulse = repeat_pulse
        self.postseq = postseq
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        
        if self.gate_info1 is not None:
            super(geophasecal, self).__init__(len(phases), infos=(control_info, zx90_info, gate_info1), **kwargs)
        else:
            super(geophasecal, self).__init__(len(phases), infos=(control_info, zx90_info), **kwargs)
        self.data.create_dataset('phases', data=phases)

    def generate(self):
        s = Sequence()

        for i, phase in enumerate(self.phases):
            r = self.control_info.rotate
            zx90 = self.zx90_info.rotate
            t = self.gate_info1.rotate
#

            for i in range(self.repeat_pulse):
                s.append(self.zx90_info.rotate(-np.pi,0))
#                s.append(r(np.pi,0))
                s.append(self.zx90_info.rotate(-np.pi,0))
#                s.append(r(np.pi,0))

            s.append(r(-np.pi/2, phase))
#            s.append(t(np.pi, 0))
        
            if self.postseq:
                s.append(self.postseq)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(1000))

        s = self.get_sequencer(s)
        seqs = s.render()
        self.seqs = seqs
        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig)
#        pi_amp = self.fit_params['period'].value / 2

        return