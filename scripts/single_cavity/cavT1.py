import numpy as np
from math import factorial
import matplotlib.pyplot as plt
from lib.math import fit
import copy
import mclient
from measurement import Measurement1D
from pulseseq.sequencer import *
from pulseseq.pulselib import *
import lmfit
import math

def poisson_decay_fit_func(params, xs, ys, n):
    '''
    Poissonian distribution given photon projection:
    alpha = alpha0 * exp(-xs / tau)

    params:
        ofs = offset
        amp = amplitude
        alpha0 = initial displacement
        tau = decay constant for energy, i.e. <n>
    '''

    alphas = params['alpha0'].value * np.exp(-xs / 2.0 / params['tau'].value)
#    nbars = params['alpha0'].value**2 * np.exp(-xs / params['tau'].value)
    nbars = alphas**2 + params['nth'].value
    vals = params['ofs'].value + params['amp'].value * nbars**n / math.factorial(n) * np.exp(-nbars)
    return ys - vals

def double_exp_decay(params, x, data):
    est = params['ofs'].value + params['amplitude'].value * np.exp(-x / params['tau'].value) + params['amplitude2'].value * np.exp(-x / params['tau2'].value)
    return data - est

def analysis(meas, data=None, fig=None): #This is a temporary analysis for double exponential by Chen
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.delays

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)

    if 1:
        params = lmfit.Parameters()
        params.add('ofs', value=np.min(ys))
        params.add('amplitude', value=np.max(ys)/2.0)
        params.add('tau', value=xs[-1], min=50.0)
        params.add('amplitude2', value=np.max(ys)/2.0)
        params.add('tau2', value=xs[-1]/4.0, min=50.0)
        result = lmfit.minimize(double_exp_decay, params, args=(xs, ys))
        lmfit.report_fit(result.params)

        weight1 = result.params['amplitude'].value / (result.params['amplitude'].value + result.params['amplitude2'].value)*100
        weight2 = 100-weight1
        text = 'Fit, tau = %.03f us +/- %.03f us (%.01f%%)\n     tau2 = %.03f us +/- %.03f us (%.01f%%)'%(
                result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0, weight1, result.params['tau2'].value/1000.0, result.params['tau2'].stderr/1000.0, weight2)
        fig.axes[0].plot(xs/1e3, -double_exp_decay(result.params, xs, 0), label=text)
        fig.axes[0].legend(loc=0)
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Time [us]')
        fig.axes[1].plot(xs, double_exp_decay(result.params, xs, ys), marker='s')

    fig.canvas.draw()
    meas.fit_params = result.params
    return result.params

def analysis_standard(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.delays
    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)

    params = lmfit.Parameters()
    if meas.bgcor:
        params.add('ofs', value=0, vary=False)
    else:
        params.add('ofs', value=np.max(ys))
    params.add('amp', value=-1.*(np.max(ys)-np.min(ys)))
    if meas.force_a0:
        params.add('alpha0', value=meas.disp, vary=False)
    else:
        params.add('alpha0', value=meas.disp)
    params.add('nth', value=0.00, min=0, max=0.4, vary=False)
    params.add('tau', value=xs[-1]/4.0, min=0)
    result = lmfit.minimize(poisson_decay_fit_func, params, args=(xs, ys, meas.proj_num))
    lmfit.report_fit(result.params)

    txt = 'Fit, Amp=%.03f\nT1=%.02f +- %.02f us\na0 = %.03f +- %.03f\nnth = %.03f +- %.03f' % (result.params['amp'].value, result.params['tau'].value/1e3, result.params['tau'].stderr/1e3, result.params['alpha0'].value, result.params['alpha0'].stderr, result.params['nth'].value, result.params['nth'].stderr)
    ys_model = -poisson_decay_fit_func(result.params, xs, 0, meas.proj_num)
    fig.axes[0].plot(xs/1e3, ys_model, label=txt)
    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Delay [us]')

    fig.axes[1].plot(xs/1e3, ys - ys_model)
    fig.canvas.draw()
    return params

class CavT1(Measurement1D):

    def __init__(self, qubit_info, cav_info, disp, delays, proj_num, seq=None, postseq=None, extra_info=None, bgcor=False,
                 force_a0 = False, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.disp = disp
        self.delays = delays
        self.proj_num = proj_num
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.xs = self.delays/1e3
        self.force_a0 = force_a0

        npoints = len(self.delays)
        if bgcor:
            npoints *= 2
        super(CavT1, self).__init__(npoints, infos=(qubit_info, cav_info), **kwargs)
        self.data.create_dataset('delays', data=self.delays)
        self.data.set_attrs(
            disp=disp,
        )

    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate_selective
        c = self.cav_info.rotate
        for i, delay in enumerate(self.delays):
            for bg in (0, 1):
                if bg and not self.bgcor:
                    continue

                s.append(self.seq)
                s.append(c(np.abs(self.disp), np.angle(self.disp)))

                s.append(Delay(delay))

                if not bg:
                    s.append(r(np.pi, X_AXIS))
                else:
                    s.append(Delay(self.qubit_info.w*4.0))
#                    s.append(Delay(5000))
                if self.postseq:
                    s.append(self.postseq)
#                s.append(Combined([
#                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ]))
                s.append(self.readout_driver.do_get_sequence(self.readout_qubit_info))
                s.append(Delay(1000))
#    
               

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def get_ys(self, data=None):
        ys = super(CavT1, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis_standard(self, data, fig)
        return self.fit_params['tau'].value
