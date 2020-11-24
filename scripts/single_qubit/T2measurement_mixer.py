# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 17:51:18 2020

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import lmfit

ECHO_NONE       = 'NONE'
ECHO_HAHN       = 'HANN'
ECHO_CPMG       = 'CMPG'
ECHO_XY4        = 'XY4'
ECHO_XY8        = 'XY8'
ECHO_XY16       = 'XY16'

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
    est = params['ofs'].value + params['amp'].value * exp * sine
    return data - est

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
    xs = meas.delays
    ys, fig = meas.get_ys_fig(data, fig)

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3, linestyle='-', markerfacecolor='red')
    fig.axes[0].errorbar(xs/1e3, ys, yerr=meas.get_errorbars(), fmt='.', 
                         markersize = 0, ecolor='grey', linewidth=1)

    amp0 = (np.max(ys) - np.min(ys)) / 2
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    f0 = np.abs(fftfs[np.argmax(fftys)])
    print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)

    params = lmfit.Parameters()
    params.add('ofs', value=np.average(ys))
    params.add('amp', value=amp0, min=0.1)
    params.add('tau', value=xs[-1], min=10, max=2e5)
    params.add('freq', value=meas.detune/1e9, min=0)
#    if meas.echotype == ECHO_NONE:
#
#        params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)  #Changed to plus sign for accommodate for amplitude RO, need a good LT solution
#
#    elif meas.echotype == ECHO_HAHN:
#        params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi) #DARIO added to fit better for echo vs plain T2
    if ys[0] < np.average(ys):
        params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)
    else:
        params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True) #Yingying changed phi0 to checking value of first point
    result = lmfit.minimize(t2_fit, params, args=(xs, ys))
#    lmfit.report_fit(params)
#    result2 = lmfit.minimize(t2_fit, result.params, args=(xs,ys))
    lmfit.report_fit(result.params)

    if meas.double_freq == False:
        fig.axes[0].plot(xs/1e3, -t2_fit(result.params, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz'%(result.params['tau'].value/1000, result.params['freq'].value*1e6))
        fig.axes[0].legend()
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Time [us]')
        fig.axes[1].plot(xs/1e3, t2_fit(result.params, xs, ys), marker='s')
        fig.canvas.draw()

    if meas.double_freq == True:

        residues = t2_fit(result.params, xs, ys)
        amp0 = (np.max(residues) - np.min(residues)) / 2
        fftys = np.abs(np.fft.fft(residues - np.average(residues)))
        fftfs = np.fft.fftfreq(len(residues), xs[1]-xs[0])
        f0 = np.abs(fftfs[np.argmax(fftys)])
        print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)

        params2 = lmfit.Parameters()
        params2.add('ofs', value=amp0)
        params2.add('amp', value=amp0, min=0)
        params2.add('tau', value=xs[-1], min=10, max=200000)
        params2.add('freq', value=meas.detune/1e9, min=0)
        params2.add('phi0', value=-np.pi/2.0, min=-1.2*np.pi, max=1.2*np.pi)
        result = lmfit.minimize(t2_fit, params2, args=(xs, residues))
        lmfit.report_fit(result.params)
#        fig.axes[1].plot(xs/1e3, -t2_fit(result.params, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz'%(result.params['tau'].value/1000, result.params['freq'].value*1e6))
        fig.axes[1].legend()

        params3 = lmfit.Parameters()
        params3.add('ofs', value=params['ofs'].value)
        params3.add('amp', value=params['amp'].value, min=0, max=params['amp'].value*2)
        params3.add('tau', value=params['tau'].value, min=10, max=200000)
        params3.add('freq', value=params['freq'].value, min=0, max=20e-3)
        params3.add('phi0', value=params['phi0'].value, min=-1.2*np.pi, max=1.2*np.pi)
        params3.add('amp2', value=result.params['amp'].value, min=0, max=params['amp'].value*2)
#        params3.add('tau2', value=result.params['tau'].value, min=10, max=200000)
        params3.add('freq2', value=result.params['freq'].value, min=0, max=20e-3)
        params3.add('phi2', value=result.params['phi0'].value, min=-1.2*np.pi, max=1.2*np.pi)

        result = lmfit.minimize(double_sin_fit, params3, args=(xs,ys))
        lmfit.report_fit(result.params)
        text = 'Fit, tau1=%.03f us, df1=%.03f kHz, amp1=%.02f \nFit, tau2=%.03f us, df2=%.03f kHz, amp2=%.02f'%(result.params['tau'].value/1000, result.params['freq'].value*1e6, result.params['amp'].value, result.params['tau'].value/1000, result.params['freq2'].value*1e6, result.params['amp2'].value)
        fig.axes[0].plot(xs/1e3, -double_sin_fit(result.params, xs, 0), label=text)
        fig.axes[0].legend()
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Time [us]')
        fig.axes[1].plot(xs/1e3, double_sin_fit(result.params, xs, ys), marker='s')
        fig.canvas.draw()
        return params3

    return result.params

class T2Measurement_mixer(Measurement1D):

    def __init__(self, qubit_info, mixer_info, mixer_info2, delays, detune=0, echotype=ECHO_NONE, necho=1,
                 double_freq=False, seq=None, postseq=None, selective=False, Qswitch_infoA=None, Qswitch_infoB=None, **kwargs):
        self.qubit_info = qubit_info
        self.mixer_info = mixer_info
        self.mixer_info2 = mixer_info2
#        self.qubit_pre = qubit_pre
        self.delays = delays
        self.xs = delays / 1e3        # For plotting purposes
        self.detune = detune
        self.echotype = echotype
        self.necho = necho
        self.double_freq=double_freq
        if seq is None:
            seq = [Trigger(250)]
        self.seq = seq
        self.postseq = postseq
        self.selective = selective     # Added 9/29 for Ramsey measuring chi
        self.QswA = Qswitch_infoA
        self.QswB = Qswitch_infoB

        super(T2Measurement_mixer, self).__init__(len(delays), infos=(qubit_info,mixer_info,mixer_info2), **kwargs)
        self.data.create_dataset('delays', data=delays)
        self.data.set_attrs(
            detune=detune,
            echotype=echotype,
            necho=necho
        )

    def get_echo_pulse(self):
        if self.selective == False:
            r = self.qubit_info.rotate
        else:
            r = self.qubit_info.rotate_selective

        if self.echotype == ECHO_NONE:
            return None

        elif self.echotype == ECHO_HAHN:
            return r(np.pi, X_AXIS)

        elif self.echotype == ECHO_CPMG:
            return r(np.pi, Y_AXIS)

        elif self.echotype == ECHO_XY4:
            return Sequence([
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
            ])

        elif self.echotype == ECHO_XY8:
            return Sequence([
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),

                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
            ])

        elif self.echo == ECHO_XY16:
            return Sequence([
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),

                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),

                r(-np.pi, X_AXIS),
                r(-np.pi, Y_AXIS),
                r(-np.pi, X_AXIS),
                r(-np.pi, Y_AXIS),

                r(-np.pi, Y_AXIS),
                r(-np.pi, X_AXIS),
                r(-np.pi, Y_AXIS),
                r(-np.pi, X_AXIS),
            ])

    def generate(self):
        s = Sequence()

        if self.selective == False:
            r = self.qubit_info.rotate
        else:
            r = self.qubit_info.rotate_selective
        e = self.get_echo_pulse()
#        if e:
#            elen = e.get_length()
#            e = Pad(e, 250, PAD_BOTH)
#            epadlen = e.get_length() - elen
#        else:
#            elen = 0

        for i, dt in enumerate(self.delays):
            s_temp = self.seq[:]
#            s.append(Constant(10, 1, chan=self.readout_info.acq_chan))
            s_temp += [r(np.pi/2, X_AXIS)]#s.append(Pad(r(np.pi/2, X_AXIS), 250, PAD_LEFT))

            # We want echos: <tau> (<tau> <echo> <tau>)^n <tau>
            if e:
                tau=int(dt/(self.necho*2 + 2))

#                s.append(Delay(tau))
#                for i in range(self.necho):
#                    s.append(Delay(tau))
#                    s.append(e)
#                    s.append(Delay(tau))
#                s.append(Delay(tau))
                
                for i in range(self.necho):
                    if tau > 0:
                        s_temp += [Delay(2*tau)]
                    s_temp += [e]
                if tau > 0:                    
                    s_temp += [Delay(2*tau)]
#                tau = int(np.round(dt / (2 * self.necho) - epadlen/2))
#                if tau < 0:
#                    s.append(Delay(dt))
#                else:
#                    s.append(Delay(tau))
#                    for i in range(self.necho - 1):
#                        s.append(e)
#                        s.append(Delay(2*tau))
#                    s.append(e)
#                    s.append(Delay(tau))

            # Plain T2
            else:
                if dt > 0:
                    s_temp += [Delay(dt)] # Very temporary, recover today Chen
#                s.append(Constant(int(dt), 1, chan='8m1'))

            # Measurement pulse
            angle = dt * 1e-9 * self.detune * 2 * np.pi
            s_temp += [r(-np.pi/2, angle)]#s.append(Pad(r(np.pi/2, angle), 250, PAD_RIGHT))

            if self.postseq:
                s_temp += [self.postseq]
#            s_temp += [Combined([
##                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                    Constant(self.readout_info.pulse_len, self.mixer_info.pi_amp, chan=self.mixer_info.channels[0]),
#                    Constant(self.readout_info.pulse_len, self.mixer_info2.pi_amp, chan=self.mixer_info2.channels[0])
#                ])]
            s_temp += [Combined([
                    Join([Delay(200),Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]),
#                   Join([Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),Delay(200)]),
                    Join([self.mixer_info.rotate(np.pi, 0),Delay(200)]),
                    Join([self.mixer_info2.rotate(np.pi, 0),Delay(200)])
#                Join([Delay(100),Constant(self.readout_info.pulse_len, self.mixer_info.pi_amp, chan=self.mixer_info.channels[0]),Delay(200)]),
                ])]
    
#            s.append(Delay(50000))

#            s.append(Repeat(Delay(1000), 20))   # wait for alazar acquisition to finish
#            s.append(Combined([
#                Repeat(Constant(5000, 0.4, chan=self.QswA.sideband_channels[0]), 60),
#                Repeat(Constant(5000, 0.4, chan=self.QswA.sideband_channels[1]), 60),
#                Repeat(Constant(5000, 0.6, chan=self.QswB.sideband_channels[0]), 60),
#                Repeat(Constant(5000, 0.6, chan=self.QswB.sideband_channels[1]), 60),
#                Repeat(Constant(5000, 1, chan='1m1'), 60),     # Readout pump tone switch
#                Repeat(Constant(5000, 0.0001, chan=5), 60),         # Qubit/Readout master switch
#            ]))

            s_temp += [Delay(2000)]
            s.append(Join(s_temp))

        s = self.get_sequencer(s)
        seqs = s.render()
#        s.plot_seqs(seqs)

        return seqs
    
    
      

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return self.fit_params['tau'].value
