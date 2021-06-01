# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 16:47:32 2020

@author: Wang_Lab
"""



import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
from lmfit.models import LinearModel, LorentzianModel
from measurement import Measurement1D
import lmfit

def Gaussfit(params, x, y):
    est = params['Amp'] * np.exp(-(x-params['freq'])**2/(2 * params['kappa']**2)) + params['off']
    
    return y - est

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.detunings

    if np.max(ys) - np.min(ys)>300:# and meas.proj_func is 'phase':

        for iphase in range(len(ys)):
            if ys[iphase] > 0:
                ys[iphase] = ys[iphase] -360    
    


    
    params = lmfit.Parameters()


    if np.max(ys) + np.min(ys) < 2 * np.average(ys):
#    if 0:
        params.add('Amp', value= -(np.max(ys)-np.min(ys)))
        params.add('freq', value=-xs[np.argmin(ys)])
    else:
        
        params.add('Amp', value= (np.max(ys)-np.min(ys)))
        params.add('freq', value=-xs[np.argmax(ys)])

    params.add('kappa', value=1e6, min = 0)#, max = 4e6)#,vary = False)
    params.add('off', value = np.average(ys))

            
#    datas = realdata[0,:]+ 1j*imagdata[0,:]    
    result = lmfit.minimize(Gaussfit, params, args=(-xs,ys))
    lmfit.report_fit(result.params)
    print ('fit freq: %s +/- %s  '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
    fig.axes[0].errorbar(-xs/1e6, ys, fmt='.', markersize = 0, ecolor='grey', linewidth=1)
#    fig.axes[0].errorbar(-xs/1e6, ys, yerr=meas.get_stes(), fmt='.', markersize = 0, ecolor='grey', linewidth=1)
    fig.axes[0].plot(-xs/1e6, -Gaussfit(result.params, -xs, 0), label='fit freq: %.03f +/- %.03f MHz \n FWHM = %.03f +/- %.03f MHz'%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6,result.params['kappa'].value/1e6,result.params['kappa'].stderr/1e6))
    fig.axes[0].legend()
    
    meas.fit_params = result.params
    
    
#    
#    fig.axes[0].plot(-xs/1e6, ys)
    fig.axes[0].set_xlabel('Detuning (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()


#
#        f = plt.figure()
#
#        if self.plot_type == SPEC:
#            ax1 = f.add_subplot(2,1,1)
#            ax2 = f.add_subplot(2,1,2)
#            for ipower, power in enumerate(self.ro_powers):
#                ax1.plot(self.q_freqs/1e6, self.ampdata[ipower,:], label='Amps, Power %.01f dB'%power)
#                ax2.plot(self.q_freqs/1e6, self.phasedata[ipower,:], label='Phase, Power %.01f dB'%power)
#            fs = self.q_freqs
#            amps = self.ampdata[0,:]
##            phases = self.phasedata[0,:]
#            f = fit.Lorentzian(fs, amps)
##            f = fit.Lorentzian(fs, phases)
#            h0 = np.max(amps)/2.0
#            w0 = 2e6
#            pos = fs[np.argmax(amps)]
#            p0 = [np.max(amps), w0*h0, pos, w0]
#            p = f.fit(p0)
#            txt = 'Center = %.03f MHz' % (p[2]/1e6,)
#            print 'Fit gave: %s' % (txt,)
#            ax1.plot(fs/1e6, f.func(p, fs), label=txt)
class CW_Stark_shift_with_mixer(Measurement1D):

    def __init__(self, qubit_info, mixer_info, mixer_info2, SS_mixer_info, phase1, detunings,damp_delay=0, seq=None, postseq=None, bgcor=False, coplay_delay=0, **kwargs):
        self.qubit_info = qubit_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.SS_mixer_info = SS_mixer_info

        self.damp_delay = damp_delay
        self.phase1 = phase1
        self.mixer_info = mixer_info
        self.mixer_info2 = mixer_info2
        self.postseq = postseq
        self.detunings = -detunings
        self.xs = detunings / 1e6       # For plot
        self.bgcor = bgcor
        self.coplay_delay=coplay_delay
        self.height = 0
        self.center = 0
        self.width=0

        npoints = len(detunings)
        if bgcor:
            npoints += 1
        super(CW_Stark_shift_with_mixer, self).__init__(npoints, residuals=False, infos=(qubit_info,mixer_info,SS_mixer_info,mixer_info2,), **kwargs)
        self.data.create_dataset('detunings', data=detunings)

    def generate(self):
        s = Sequence()
        slope = .00513
        if self.mixer_info.deltaf == 0:
            
            ro = (Combined([
                Join([Delay(200),Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]),
                Join([Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),Delay(200)]),
                Join([Constant(self.readout_info.pulse_len, self.mixer_info.pi_amp, chan=self.mixer_info.channels[0]),Delay(200)]),
                Join([Constant(self.readout_info.pulse_len, self.mixer_info2.pi_amp, chan=self.mixer_info2.channels[0]),Delay(200)])

            ]))
        else:
            ro = (Combined([
                Join([Delay(200),Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]),
#                Join([Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),Delay(200)]),
                Join([self.mixer_info.rotate(np.pi, 0),Delay(200)]),
                Join([self.mixer_info2.rotate(np.pi, 0),Delay(200)])

            ]))
        if self.SS_mixer_info.deltaf == 0:
            stark = (Combined([
#                Join([Constant(int(self.SS_mixer_info.w) + 100, 1, chan=self.readout_info.readout_chan)]),
                Join([Constant(int(10000 + self.qubit_info.w_selective*4), self.SS_mixer_info.pi_amp, chan=self.SS_mixer_info.channels[0]),Delay(5)]),
#                Join([Delay(100),Constant(int(self.SS_mixer_info2.w), self.SS_mixer_info2.pi_amp, chan=self.SS_mixer_info2.channels[0])]),

            ]))
        else:
#            stark = (Combined([
##                Constant(int(self.SS_mixer_info1.w) , 1, chan=self.readout_info.readout_chan),
##                Join([Delay(100),Constant(int(self.SS_mixer_info.w), self.SS_mixer_info.pi_amp, chan=self.SS_mixer_info.sideband_channels[0])]),
##                Join([Delay(100),Constant(int(self.SS_mixer_info2.w), self.SS_mixer_info2.pi_amp, chan=self.SS_mixer_info2.sideband_channels[0])]),
#                Join([self.SS_mixer_info1.rotate(np.pi*np.exp(-slope*self.damp_delay), self.phase1),Delay(10)]),
#                Join([self.SS_mixer_info2.rotate(np.pi, 0),Delay(10)])
#            ]))
            stark = Join([Constant(int(10000 + self.qubit_info.w_selective*4), self.SS_mixer_info.pi_amp, chan=self.SS_mixer_info.sideband_channels[0]),Delay(5)])
#            stark = Join([self.SS_mixer_info1.rotate(np.pi, self.phase1),self.SS_mixer_info1.rotate(np.pi, self.phase1 +3.141)])
        if self.bgcor:
            plen = self.qubit_info.rotate_selective.base(np.pi, 0).get_length()
            s.append(Join([self.seq, Delay(plen), ro]))

        for i, df in enumerate(self.detunings):
#        for df in self.detunings:
            g = DetunedSum(self.qubit_info.rotate_selective.base, self.qubit_info.w_selective, chans=self.qubit_info.sideband_channels)
            if df != 0:
                period = 1e9 / df
            else:
                period = 1e50
            g.add(self.qubit_info.pi_amp_selective, period)
            g_delay = Join([Delay(10000),g(),Delay(5)])
            s.append(Join([
                self.seq,
                Combined([stark,
                g_delay]),
               
            ]))
#            s.append(self.seq)
#            s.append(stark)
#            s.append(g())

            if self.postseq:
                s.append(self.postseq)
            s.append(ro)
            #Ebru, adding the 20000 delay
            s.append(Delay(20000))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs
    

    def get_ys(self, data=None):
        ys = super(CW_Stark_shift_with_mixer, self).get_ys(data)
        if self.bgcor:
            return ys[1:] - ys[0]
        return ys

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
