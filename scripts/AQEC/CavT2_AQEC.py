import numpy as np
from math import factorial
import matplotlib.pyplot as plt
from lib.math import fit
import copy
import mclient
from measurement import Measurement1D
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from pulseseq import OCTlib
import lmfit
import math


def t2_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-c * x) * sin(d * x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    exp = np.exp(-(x / params['tau'].value))
    est = params['ofs'].value + params['amp'].value * exp * sine + params['slope'] * x
    return data - est

def double_exp_sin_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-c * x) * sin(d * x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
#    est = params['ofs'].value + params['amplitude'].value * np.exp(-x / params['tau'].value) + params['amplitude2'].value * np.exp(-x / params['tau2'].value)
    exp1 = np.exp(-x / params['tau1'].value)
    exp2 = np.exp(-x / params['tau2'].value)
    est = params['ofs'].value + (params['amp1'].value * exp1 + params['amp2'].value * exp2) * sine
    return data - est

def double_sin_fit(params, x, data):
    '''
    Double exponentially decaying sine
    fit function: of + a1 * exp(-tau1 * x) * sin(f1 * x + phi1) + a2 * exp(-tau2 * x) * cos(f2 * x + phi2)
    '''
    exp1 = np.exp(-(x / params['tau'].value))
    exp2 = np.exp(-(x / params['tau2'].value))
    sin1 = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    sin2 = np.sin(2 * np.pi * x * params['freq2'].value + params['phi2'].value)
    est = params['ofs'].value + params['amp'].value * exp1 * sin1 + params['amp2'].value * exp2 * sin2
    return data - est

def analysis_2tau(meas, data=None, fig=None):  #Temporary analysis for double exponential decay by Chen
    xs = meas.delays
    ys, fig = meas.get_ys_fig(data, fig)

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)

    amp0 = (np.max(ys) - np.min(ys)) / 2
    off0 = (np.max(ys) + np.min(ys)) / 2
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    f0 = np.abs(fftfs[np.argmax(fftys)])
    print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)

    params = lmfit.Parameters()
    params.add('ofs', value=off0)
    params.add('amp1', value=amp0/2, min=0)
    params.add('amp2', value=amp0/2, min=0)
    params.add('tau1', value=xs[-1]/100, min=10, max=4e6)
    params.add('tau2', value=xs[-1], min=10, max=4e6)
    params.add('freq', value=f0, min=0)
    params.add('phi0', value=0, min=-1.2*np.pi, max=1.2*np.pi)
    result = lmfit.minimize(double_exp_sin_fit, params, args=(xs, ys))
    lmfit.report_fit(result.params)

    fig.axes[0].plot(xs/1e3, -double_exp_sin_fit(result.params, xs, 0), label='Fit, tau1=%.03f us, tau2=%.03f us, df=%.03f kHz'
            %(result.params['tau1'].value/1000, result.params['tau2'].value/1000, result.params['freq'].value*1e6))
    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')
    fig.axes[1].plot(xs/1e3, double_exp_sin_fit(result.params, xs, ys), marker='s')
    fig.canvas.draw()

    return result.params

def analysis(meas, data=None, fig=None): 
    xs = meas.delays
    ys, fig = meas.get_ys_fig(data, fig)

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)

    amp0 = (np.max(ys) - np.min(ys)) / 2
    off0 = (np.max(ys) + np.min(ys)) / 2
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    f0 = np.abs(fftfs[np.argmax(fftys)])
    print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)

    params = lmfit.Parameters()
    params.add('ofs', value=off0)
    params.add('amp', value=amp0, min=0)
    params.add('tau', value=xs[-1]/2, min=10, max=4e6)
    params.add('freq', value=f0, min=0)
    params.add('phi0', value=np.pi/2, min=-2*np.pi, max=2*np.pi)
    params.add('slope', value = 0)
    result = lmfit.minimize(t2_fit, params, args=(xs, ys))
    lmfit.report_fit(result.params)

    fig.axes[0].plot(xs/1e3, -t2_fit(result.params, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz'%(result.params['tau'].value/1000, result.params['freq'].value*1e6))
    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')
    fig.axes[1].plot(xs/1e3, t2_fit(result.params, xs, ys), marker='s')
    fig.canvas.draw()

    if meas.double_freq == True:

        residues = t2_fit(params, xs, ys)
        amp0 = (np.max(residues) - np.min(residues)) / 2
        fftys = np.abs(np.fft.fft(residues - np.average(residues)))
        fftfs = np.fft.fftfreq(len(residues), xs[1]-xs[0])
        f0 = np.abs(fftfs[np.argmax(fftys)])
        print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)

        params2 = lmfit.Parameters()
        params2.add('ofs', value=amp0)
        params2.add('amp', value=amp0, min=0)
        params2.add('tau', value=xs[-1], min=10, max=200000)
        params2.add('freq', value=f0, min=0)
        params2.add('phi0', value=0, min=-1.2*np.pi, max=1.2*np.pi)
        result = lmfit.minimize(t2_fit, params2, args=(xs, residues))
        lmfit.report_fit(params2)
        fig.axes[1].plot(xs/1e3, -t2_fit(params2, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz'%(params2['tau'].value/1000, params2['freq'].value*1e6))
        fig.axes[1].legend()

        params3 = lmfit.Parameters()
        params3.add('ofs', value=params['ofs'].value)
        params3.add('amp', value=params['amp'].value, min=0)
        params3.add('tau', value=params['tau'].value, min=10, max=200000)
        params3.add('freq', value=params['freq'].value, min=0)
        params3.add('phi0', value=params['phi0'].value, min=-1.2*np.pi, max=1.2*np.pi)
        params3.add('amp2', value=params2['amp'].value, min=0)
        params3.add('tau2', value=params2['tau'].value, min=10, max=200000)
        params3.add('freq2', value=params2['freq'].value, min=0)
        params3.add('phi2', value=params2['phi0'].value, min=-1.2*np.pi, max=1.2*np.pi)

        result = lmfit.minimize(double_sin_fit, params3, args=(xs,ys))
        lmfit.report_fit(params3)
        text = 'Fit, tau1=%.03f us, df1=%.03f kHz, amp1=%.02f \nFit, tau2=%.03f us, df2=%.03f kHz, amp2=%.02f'%(params3['tau'].value/1000, params3['freq'].value*1e6, params3['amp'].value, params3['tau2'].value/1000, params3['freq2'].value*1e6, params3['amp2'].value)
        fig.axes[0].plot(xs/1e3, -double_sin_fit(params3, xs, 0), label=text)
        fig.axes[0].legend()
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Time [us]')
        fig.axes[1].plot(xs/1e3, double_sin_fit(params3, xs, ys), marker='s')
        fig.canvas.draw()
        return params3

    return result.params


class CavT2_AQEC(Measurement1D):

    def __init__(self, qubit_info, cav_info, disp, delays, comb_list = None, t_ge=0, detune=0, seq=None, postseq=None,
                 mod=1, double_freq=False, bgcor=False, meas_type='wigner', **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.disp = disp
        self.delays = delays
        self.comb_list = comb_list
        self.detune = detune
        self.double_freq=double_freq
        self.bgcor = bgcor
        if seq is None:
            seq = [Trigger(250)]
        self.seq = seq
        self.postseq = postseq
        self.xs = self.delays/1e3
        self.t_ge = t_ge
        self.mod = mod
        self.meas_type = meas_type
        
        infos = [qubit_info, cav_info]
        if comb_list is not None:
            infos += [comb.info for comb in comb_list]

        npoints = len(self.delays)
        if bgcor:
            npoints *= 2
        super(CavT2_AQEC, self).__init__(npoints, infos=infos, **kwargs)
        self.data.create_dataset('delays', data=self.delays)
        if comb_list is not None:
            self.data.set_attrs(
                disp=disp,
                fwm_amps = comb_list[0].amps,
                stark_shift = comb_list[0].stark_shift
            )

    def generate(self): # NEW OCT 01 encoding/decoding

        
        s = Sequence()
        ge = self.qubit_info.rotate
        ges = self.qubit_info.rotate_selective
        c = self.cav_info.rotate
        for i, delay in enumerate(self.delays):
            for i_bg in range(2):
                if i_bg == 1 and not self.bgcor:
                    continue

                temp_seq = self.seq[:]
                if delay > 0:
                    if self.comb_list is not None:
                        poly_seq = []
                        for comb in self.comb_list:
                            poly_seq += comb.get_poly_seq(delay - comb.sigma*4, 0)
                        temp_seq += [Combined(poly_seq)]
                    else:
                        temp_seq += [Delay(delay)]
                    
                dphi = 2 * np.pi * self.detune * delay * 1e-9 / self.mod
                temp_seq += [c(self.disp,dphi)]
                
                if self.meas_type == 'wigner':
                    if i_bg == 0:
                        temp_seq += [ge(np.pi/2, X_AXIS)]
                        if self.t_ge > 0:
                            temp_seq += [Delay(self.t_ge)]
                        temp_seq += [ge(np.pi/2, X_AXIS)]
                    else:
                        temp_seq += [ge(np.pi/2, X_AXIS)]
                        if self.t_ge > 0:
                            temp_seq += [Delay(self.t_ge)]
                        temp_seq += [ge(-np.pi/2, X_AXIS)]
                elif self.meas_type == 'qfunc':
                    if i_bg == 0:
                        temp_seq += [ges(np.pi, 0)]

                if self.postseq:
                    temp_seq += [self.postseq]

                temp_seq += [Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ])]
                s.append(Join(temp_seq))

        s = self.get_sequencer(s)
        seqs = s.render(debug=False)
        return seqs

    



    def get_ys(self, data=None):
        ys = super(CavT2_AQEC, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return self.fit_params
