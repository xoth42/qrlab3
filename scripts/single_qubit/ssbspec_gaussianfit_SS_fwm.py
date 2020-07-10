# -*- coding: utf-8 -*-
"""
Created on Tue May 26 16:11:34 2020

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

    params.add('kappa', value=1.01e6, min = 0)#, max = 4e6)#,vary = False)
    params.add('off', value = np.average(ys))

            
#    datas = realdata[0,:]+ 1j*imagdata[0,:]    
    result = lmfit.minimize(Gaussfit, params, args=(-xs,ys))
    lmfit.report_fit(result.params)
    print ('fit freq: %s +/- %s  '%(result.params['freq'].value,result.params['freq'].stderr))


    fig.axes[0].plot(-xs/1e6, -Gaussfit(result.params, -xs, 0), label='fit freq: %s +/- %s Hz '%(result.params['freq'].value,result.params['freq'].stderr))
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
class SSBSpec_Gaussianfit_SS_fwm(Measurement1D):

    def __init__(self, qubit_info, fwm_info, detunings, seq=None, postseq=None, bgcor=False, coplay_delay=0, **kwargs):
        self.qubit_info = qubit_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.detunings = -detunings
        self.xs = detunings / 1e6       # For plot
        self.bgcor = bgcor
        self.coplay_delay=coplay_delay
        self.height = 0
        self.center = 0
        self.width=0
        self.fwm_info=fwm_info

        npoints = len(detunings)
        if bgcor:
            npoints += 1
        super(SSBSpec_Gaussianfit_SS_fwm, self).__init__(npoints, residuals=False, infos=(qubit_info,fwm_info), **kwargs)
        self.data.create_dataset('detunings', data=detunings)

    def generate(self):
        s = Sequence()

        ro =Combined([
            Join([Delay(200),Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]),
            Join([Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),Delay(200)]),
        ])

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
            
            delaytime = 10000
            delaytime2 = 30
            pulselen = int(4 * self.qubit_info.w_selective + delaytime+delaytime2)
#            pulselen = 40000
            gS = Combined([
                    Join([Delay(delaytime),g(),Delay(delaytime2)]),
                    Constant(pulselen , self.fwm_info.pi_amp , chan = self.fwm_info.sideband_channels[0]),
            ])

            s.append(Join([
                self.seq,
                gS,
                Delay(100)
            ]))

            if self.postseq:
                s.append(self.postseq)
            s.append(ro)
            #Ebru, adding the 20000 delay
            s.append(Delay(200))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs
    

    def get_ys(self, data=None):
        ys = super(SSBSpec_Gaussianfit_SS_fwm, self).get_ys(data)
        if self.bgcor:
            return ys[1:] - ys[0]
        return ys

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
