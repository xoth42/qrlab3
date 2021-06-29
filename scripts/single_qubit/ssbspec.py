import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
from lib.math import fit
import lmfit

def double_gaussian(params, x, data):
    dx1 = x-params['center1']
    dx2 = x-params['center2']
    est = (params['background'] + params['amp1'] * np.exp(-np.power(dx1, 2.) / (2 * np.power(params['sigma'], 2.)))
                                + params['amp2'] * np.exp(-np.power(dx2, 2.) / (2 * np.power(params['sigma'], 2.))))
    return data - est

def single_gaussian(params, x, data):
    dx1 = x-params['center1']
    est = (params['background'] + params['amp1'] * np.exp(-np.power(dx1, 2.) / (2 * np.power(params['sigma'], 2.))))
    return data - est

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = -meas.detunings
    fig.axes[0].plot(xs/1e6, ys, '.')
    
    try: # This is a placeholder until stes is implemented w/ Alazar.
        fig.axes[0].errorbar(xs/1e6, ys, yerr=meas.get_errorbars(), fmt='.', 
                         markersize = 0, ecolor='grey', linewidth=1)
    except:
        print('passed no errorbars')
        
    fig.axes[0].set_xlabel('Detuning (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()

    if 0: #For double Gaussian fit - qubit 2
        params = lmfit.Parameters()
        params.add('background', value=max(ys), max=max(ys)+0.5)
        params.add('amp1', value=-(np.max(ys)-np.min(ys))/1.2)
        params.add('amp2', value=-(np.max(ys)-np.min(ys))/1.2)
        params.add('sigma', value=(xs[-1]-xs[0])/12, max=(xs[-1]-xs[0])/2)
        params.add('center1', value=xs[np.argmin(ys)])
        params.add('center2', value=(xs[np.argmin(ys)]+xs[-1])/2)
            
        result = lmfit.minimize(double_gaussian, params, args=(xs, ys))
        lmfit.report_fit(result.params)
    
        fig.axes[0].plot(xs/1e6, -double_gaussian(result.params, xs, 0))
        fig.canvas.draw()
        return result.params



    if 0: #For double Gaussian fit - qubit1
        params = lmfit.Parameters()
        params.add('background', value=min(ys), min=min(ys)+0.5)
        params.add('amp1', value=(np.max(ys)-np.min(ys))/1.2)
        params.add('amp2', value=(np.max(ys)-np.min(ys))/1.2)
        params.add('sigma', value=(xs[-1]-xs[0])/12, max=(xs[-1]-xs[0])/2)
        params.add('center1', value=xs[np.argmax(ys)], min=xs[0], max=xs[-1])
        params.add('center2', value=(xs[np.argmax(ys)]-xs[-1])/2, min=xs[0], max=xs[-1])
            
        result = lmfit.minimize(double_gaussian, params, args=(xs, ys))
        lmfit.report_fit(result.params)
    
        fig.axes[0].plot(xs/1e6, -double_gaussian(result.params, xs, 0))
        fig.canvas.draw()
        return result.params

#













    if 1: #For single Gaussian fit
        ys2 = np.abs(ys - np.mean(ys))
        ii = np.argmax(ys2)
        
        
        params = lmfit.Parameters()
<<<<<<< HEAD
#        params.add('background', value=min(ys), min=min(ys)-5) #+np.absolute(min(ys))*0.5)
#        params.add('amp1', value=-(np.min(ys)-np.max(ys))/1.2, min=0) #Chen reverted to positive peak 6/27
#        params.add('sigma', value=(xs[-1]-xs[0])/12, max=(xs[-1]-xs[0])/2)
#        params.add('center1', value=xs[np.argmax(ys)], min=xs[0], max=xs[-1])
        
        
        params.add('background', value=np.mean(ys)) #+np.absolute(min(ys))*0.5)
        params.add('amp1', value=ys[ii]) #Chen reverted to positive peak 6/27
        params.add('sigma', value=np.abs(xs[-1]-xs[0])/5)
        params.add('center1', value=xs[ii])

        #alternative fit params  - LLG
#        params.add('background', value=min(ys), min=min(ys)-5) #+np.absolute(min(ys))*0.5)
#        params.add('amp1', value=(np.min(ys)-np.max(ys))/1.2) #Chen reverted to positive peak 6/27
#        params.add('sigma', value=(xs[-1]-xs[0])/12, max=(xs[-1]-xs[0])/2)
#        params.add('center1', value=xs[np.argmin(ys)], min=xs[0], max=xs[-1])
        
        result = lmfit.minimize(single_gaussian, params, args=(xs, ys))
        lmfit.report_fit(result.params)
    
        fig.axes[0].plot(xs/1e6, -single_gaussian(result.params, xs, 0))
        fig.canvas.draw()
        return result.params           
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

class SSBSpec(Measurement1D):

    def __init__(self, qubit_info, detunings, seq=None, postseq=None, bgcor=False, 
                 coplay_delay=0, reset_seq=None, **kwargs):
        self.qubit_info = qubit_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.detunings = -detunings
        self.xs = detunings / 1e6       # For plot
        self.bgcor = bgcor
        self.coplay_delay=coplay_delay
        self.reset_seq = reset_seq

        npoints = len(detunings)
        if bgcor:
            npoints += 1
        super(SSBSpec, self).__init__(npoints, residuals=False, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('detunings', data=detunings)

    def generate(self):
        s = Sequence()

#        ro = Combined([
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#        ])

        if self.bgcor:
            plen = self.qubit_info.rotate_selective.base(np.pi, 0).get_length()

            
            s.append(Join([self.seq, Delay(plen)]))
            if self.post_seq is not None:
                s.append(self.postseq)
            s.append(self.readout_driver.do_get_sequence())


        for i, df in enumerate(self.detunings):
#        for df in self.detunings:
            g = DetunedSum(self.qubit_info.rotate_selective.base, self.qubit_info.w_selective, chans=self.qubit_info.sideband_channels)
            if df != 0:
                period = 1e9 / df
            else:
                period = 1e50
            g.add(self.qubit_info.pi_amp_selective, period)

            s.append(Join([
                self.seq,
                g(),
            ]))

            if self.postseq:
                s.append(self.postseq)

            s.append(self.readout_driver.do_get_sequence())


            #Ebru, adding the 20000 delay
            if self.reset_seq is not None:
                s.append(self.reset_seq)
            s.append(Delay(2000))
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs
    

    def get_ys(self, data=None):
        ys = super(SSBSpec, self).get_ys(data)
        if self.bgcor:
            return ys[1:] - ys[0]
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        self.fig = fig

