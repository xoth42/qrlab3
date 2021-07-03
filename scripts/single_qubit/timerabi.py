import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import matplotlib.pyplot as plt
import copy
import mclient
import lmfit

FIT_AMP         = 'AMP'         # Fit simple sine wave
FIT_AMPFUNC     = 'AMPFUNC'     # Try to fit amplitude curve based on pi/2 and pi amp
FIT_PARABOLA    = 'PARABOLA'    # Fit a parabola (to determine min/max pos)

def fit_timerabi(params, x, data):
    est = (params['ofs'].value - np.exp(-x / params['tau']) *params['amp'].value 
            * np.cos(2*np.pi*x / params['period'].value + params['phase'].value))
    return data  - est

def double_sin_fit(params, x, data):
    '''
    Double exponentially decaying sine
    fit function: of + a1 * exp(-tau1 * x) * sin(f1 * x + phi1) + a2 * exp(-tau2 * x) * cos(f2 * x + phi2)
    '''
    exp1 = np.exp(-(x / params['tau'].value))
    exp2 = np.exp(-(x / params['tau'].value))#exp2 = np.exp(-(x / params['tau2'].value))  #Chen changed to single tau for both frequencies 8/24/19
    sin1 = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    sin2 = np.sin(2 * np.pi * x * params['freq2'].value + params['phi2'].value)
    est = params['ofs'].value + params['amp'].value * exp1 * sin1 + params['amp2'].value * exp2 * sin2
    return data - est


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.times

    fig.axes[0].plot(xs, ys, 'ks', ms=3)

    amp0 = (np.max(ys) - np.min(ys)) / 2
    if ys[0]>np.average(ys):
        amp0 = -amp0
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    period0 = 1 / np.abs(fftfs[np.argmax(fftys)])

    params = lmfit.Parameters()
    params.add('ofs', value=np.average(ys))
    params.add('amp', value=amp0)
    params.add('phase', value=0, vary=False)#min=-np.pi, max=np.pi)
    params.add('tau', value=np.max(xs))
    params.add('period', value=period0, min=0)
    
    result = lmfit.minimize(fit_timerabi, params, args=(xs, ys))
    # stderr of 0 is none. replace with other line when using actual data
    #txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.06f' % (result.params['amp'].value, 0, result.params['period'].value, 0, result.params['period'].value/2 )
    txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.06f' % (result.params['amp'].value, 
                                                                             result.params['amp'].stderr, 
                                                                             result.params['period'].value, 
                                                                             result.params['period'].stderr, 
                                                                             result.params['period'].value/2 )
    fig.axes[0].plot(xs, -fit_timerabi(result.params, xs, 0), label=txt)
    fig.axes[0].plot(xs, -fit_timerabi(result.params, xs, 0))
    fig.axes[1].plot(xs, fit_timerabi(result.params, xs, ys), marker='s')

#    lmfit.report_fit(params)
    lmfit.report_fit(result.params)

    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Pulse time')
    fig.axes[0].legend(loc=0)

    fig.canvas.draw()
    return result.params

class TimeRabi(Measurement1D):

    def __init__(self, qubit_info, times, amp, update=False, seq=None, r_axis=0, fix_phase=True,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, fit_type=FIT_AMP, **kwargs):
        self.qubit_info = qubit_info
        self.times = times
        self.xs = times
        self.amp = amp
        self.update_ins = update
        if seq is None:
            seq = Trigger(1000)
        self.seq = seq
        self.postseq = postseq
        self.fix_phase = fix_phase
        self.fix_period = fix_period
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis
        self.fit_type = fit_type
        self.selective = selective

        super(TimeRabi, self).__init__(len(times), infos=(qubit_info,), **kwargs)
        self.data.create_dataset('times', data=times)

    def generate(self):
        s = Sequence()

        for plen in self.times:
            
            s.append(self.seq)
#            g = DetunedSum(self.qubit_info.rotate.base, plen, chans=self.qubit_info.sideband_channels)
#            period = 1e50 #This is basically infinity
#            g.add(self.amp, period)

#            s.append(Join([
#                self.seq,
#                g(),
#            ]))
#            s.append(g())
            
            chs = self.qubit_info.sideband_channels
            if plen > 0:
                s.append(Repeat(Constant(int(plen), self.amp, chan=chs[0]),self.repeat_pulse))
#                s.append(Repeat(Constant(int(plen), self.amp, chan='3m1'),self.repeat_pulse))

                #            s.append(Combined([
#                Constant(int(plen), self.amp, chan=chs[0]),
#                Constant(int(plen), self.amp, chan=chs[1])
#            ]))
            
            if self.postseq:
                s.append(self.postseq)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
    
    
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs


    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig)
