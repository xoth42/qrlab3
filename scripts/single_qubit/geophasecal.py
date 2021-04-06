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

    def __init__(self, ge_info, test_info, phases, test_info2=None, seq=None, wait_reference = False, wait_time = None, repeat_pulse=1, delay=0, postseq = None,
                 **kwargs):
        self.ge_info = ge_info
        self.test_info = test_info
        self.test_info2 = test_info2
        self.phases = phases
        self.delay = delay

        self.xs = phases
        self.wait_reference = wait_reference
        self.wait_time = wait_time
        self.repeat_pulse = repeat_pulse
        self.postseq = postseq
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        
        if self.test_info2 is not None:
            super(geophasecal, self).__init__(len(phases), infos=(ge_info, test_info, test_info2), **kwargs)
        else:
            super(geophasecal, self).__init__(len(phases), infos=(ge_info, test_info), **kwargs)
        self.data.create_dataset('phases', data=phases)

    def generate(self):
        s = Sequence()

        r = self.ge_info.rotate
        r_test = self.test_info.rotate
        test_pulse = r_test(np.pi, 0)
        if self.test_info2 is not None:
            r_test2 = self.test_info2.rotate
            test_pulse2 = r_test2(np.pi, 0)

        for i, phase in enumerate(self.phases):
            s.append(Join([self.seq, r(np.pi/2, 0), Delay(5)]))            

#            if self.test_info2 is not None:
#                for j in range(self.repeat_pulse):
#                    s.append(Combined([test_pulse, test_pulse2]))
#                    s.append(test_pulse2)
#            else:
#                s.append(Repeat(test_pulse, self.repeat_pulse))
#
            if self.wait_reference == True:
                s.append(Delay(self.wait_time))
            else:
                s.append(Repeat(self.test_info.rotate(np.pi,0), self.repeat_pulse))

            s.append(r(-np.pi/2, phase))
        
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
        pi_amp = self.fit_params['amp'].value

        return pi_amp