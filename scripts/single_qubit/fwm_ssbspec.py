
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


    fig.axes[0].plot(-xs/1e6, -Gaussfit(result.params, -xs, 0), label='fit freq: %s +/- %s MHz '%(result.params['freq'].value/1e6,result.params['freq'].stderr/1e6))
    fig.axes[0].legend()
    
    meas.fit_params = result.params
    
    
#    
#    fig.axes[0].plot(-xs/1e6, ys)
    fig.axes[0].set_xlabel('Detuning (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()

        
#    f = fit.Lorentzian(xs, ys)
#    if 0:
#        h0 = np.max(ys)-np.min(ys)
#        w0 = 0.05e6
#        pos = xs[np.argmax(ys)]
#        p0 = [np.min(ys), w0*h0, pos, w0]
#    if 1:
#        h0 = np.min(ys)-np.max(ys)
#        w0 = 0.05e6
#        pos = xs[np.argmin(ys)]
#        p0 = [np.max(ys), w0*h0, pos, w0]
#        p = f.fit(p0)
#    txt = 'Center = %.03f MHz, FWHM = %.03f MHz' % (/1e6, p[3]/1e6)
#    plt.plot(-xs/1e6, f.func(p, xs), label=txt)
#    print 'Fit gave: %s' % (txt,)

class FWM_SSBSpec(Measurement1D):

    def __init__(self, ge_info, ef_info, fwm_info, detunings, seq=None, postseq=None, bgcor=False, coplay_delay=0, **kwargs):
        self.ge_info = ge_info
        self.ef_info = ef_info
        self.fwm_info = fwm_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.detunings = -detunings
        self.xs = detunings / 1e6       # For plot
        self.bgcor = bgcor
        self.coplay_delay=coplay_delay


        npoints = len(detunings)
        if bgcor:
            npoints += 1
        super(FWM_SSBSpec, self).__init__(npoints, residuals=False, infos=(ge_info,ef_info, fwm_info,), **kwargs)
        self.data.create_dataset('detunings', data=detunings)

    def generate(self):
        s = Sequence()
        r = self.ge_info.rotate
        r_ef = self.ef_info.rotate
        ro = Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
        ])

        if self.bgcor:
            plen = self.fwm_info.rotate.base(np.pi, 0).get_length()
            s.append(Join([self.seq, Delay(plen), ro]))

        for i, df in enumerate(self.detunings):
#        for df in self.detunings:
            g = DetunedSum(self.fwm_info.rotate.base, self.fwm_info.w, chans=self.fwm_info.sideband_channels)
            if df != 0:
                period = 1e9 / df
            else:
                period = 1e50
            g.add(self.fwm_info.pi_amp, period)

            s.append(Join([
                self.seq,
                r(np.pi, 0),
                r_ef(np.pi, 0),
                g(),
            ]))

            if self.postseq is None:
                s.append(r(np.pi/2, 0))
            else:
                s.append(self.postseq)
            s.append(ro)
            
            #Ebru, adding the 20000 delay
            s.append(Delay(2000))
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs
    

    def get_ys(self, data=None):
        ys = super(FWM_SSBSpec, self).get_ys(data)
        if self.bgcor:
            return ys[1:] - ys[0]
        return ys

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
        self.fig = fig

