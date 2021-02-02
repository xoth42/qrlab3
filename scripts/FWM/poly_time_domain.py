"""
time domain of multiple tones read out on mulitple qubit frequencies


Jeff Gertler
"""


import numpy as np
from math import factorial
import matplotlib.pyplot as plt
#from lib.math import fit
from measurement import Measurement1D
from pulseseq.sequencer import *
from pulseseq.pulselib import *
import lmfit
import objectsharer as objsh


def exp_decay(params, x, data):
    est = params['ofs'] + params['amp'] * np.exp(-x / params['tau'].value)
    return data - est

def gompertz(params, x, data):
    est = params['ofs'] + params['amp'] * np.exp(-params['delay'] * np.exp(-x / params['tau']))
    return data - est

def two_scale_exp(params, x, data):
#    a = 1/(params['tau_avg']+params['tau_diff']/2)
#    b = 1/(params['tau_avg']-params['tau_diff']/2)
    a = params['gamma1']
    b = params['gamma2']
    norm_factor = (a-b)**2 / (2*a*b*(a+b))
    est = params['ofs'] + params['amp']*( 0.5/a*(1-np.exp(-2*a*x)) + 0.5/b*(1-np.exp(-2*b*x)) - 2/(a+b)*(1-np.exp(-(a+b)*x)) ) / norm_factor
    return data - est

def two_scale_exp2(params, x, data):
#    a = 1/(params['tau_avg']+params['tau_diff']/2)
#    b = 1/(params['tau_avg']-params['tau_diff']/2)
    a = params['gamma_avg']+params['gamma_diff']
    b = params['gamma_avg']-params['gamma_diff']
    norm_factor = (a-b)**2 / (2*a*b*(a+b))
    est = params['ofs'] + params['amp']*( 0.5/a*(1-np.exp(-2*a*x)) + 0.5/b*(1-np.exp(-2*b*x)) - 2/(a+b)*(1-np.exp(-(a+b)*x)) ) / norm_factor
    return data - est

#def critical_osc(params, x, data):
#
#    est = params['ofs'] + params['amp']*
#    a = params['gamma_avg']+params['gamma_diff']
#    b = params['gamma_avg']-params['gamma_diff']
#    norm_factor = (a-b)**2 / (2*a*b*(a+b))
#    est = params['ofs'] + params['amp']*( 0.5/a*(1-np.exp(-2*a*x)) + 0.5/b*(1-np.exp(-2*b*x)) - 2/(a+b)*(1-np.exp(-(a+b)*x)) ) / norm_factor
#    return data - est
    
def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.delays
    num_delays = len(xs)

    
    for i, info in enumerate(meas.qubit_list):
        if meas.bgcor:
            YS =  ys[i*num_delays : (i+1)*num_delays] - ys[-num_delays:]
        else:
            YS =  ys[i*num_delays : (i+1)*num_delays]

        
        try: # This is a placeholder until stes is implemented w/ Alazar.
            fig.axes[0].errorbar(xs/1e3, YS, yerr=meas.get_errorbars(), fmt='.', 
                             markersize = 0, ecolor='grey', linewidth=1)
        except:
            print('passed no errorbars')  
        fig.axes[0].plot(xs/1e3, YS, ms=3, label = info.insname)
        
        
        print 'average YS=', YS.mean()
        
        if 1: # gompertz fit
            XS = xs
            params = lmfit.Parameters()
            params.add('ofs', value=YS[0])
            params.add('amp', value=YS[-1])
            params.add('delay', value = 5)
            params.add('tau', value=XS[-1]/2, min=50.0)
            result = lmfit.minimize(gompertz, params, args=(XS, YS))
    #        lmfit.report_fit(params)
    #        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
            lmfit.report_fit(result.params)
            
            midpoint = result.params['ofs'] + result.params['amp']/2
            half_life = -result.params['tau'] * np.log(-1.0/result.params['delay'] * np.log((midpoint - result.params['ofs'])/result.params['amp']))
    
            fig.axes[0].plot(XS/1e3, -gompertz(result.params, XS, 0), label='Fit, tau = %.03f us +/- %.03f us \n delay = %.03f ? +/- %.03f ? \n halflife = %.03f us'
                    %(result.params['tau'].value/1e3, result.params['tau'].stderr/1e3, result.params['delay'].value, result.params['delay'].stderr, half_life/1e3))
            fig.axes[0].legend(loc=0)
            fig.axes[0].set_ylabel('Intensity [AU]')
            fig.axes[0].set_xlabel('Time [us]')
            fig.axes[1].plot(XS/1e3, gompertz(result.params, XS, YS), marker='s')
            
        if 0: # exponential fit
            Xs = xs[meas.skip_points:num_delays]
            YS = YS[meas.skip_points:num_delays]
            params = lmfit.Parameters()
            params.add('ofs', value=np.min(YS))
            params.add('amp', value=np.max(YS))
            params.add('tau', value=Xs[-1]/2.0, min=50.0)
            result = lmfit.minimize(exp_decay, params, args=(Xs, YS))
    #        lmfit.report_fit(params)
    #        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
            lmfit.report_fit(result.params)
    
            fig.axes[0].plot(Xs/1e3, -exp_decay(result.params, Xs, 0), label='Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
            fig.axes[0].legend(loc=0)
            fig.axes[0].set_ylabel('Intensity [AU]')
            fig.axes[0].set_xlabel('Time [us]')        


        if 0: # two-scale exponential fit overdamped but near critical damping 
            XS = xs
            params = lmfit.Parameters()
            params.add('ofs', value=YS[0], vary=True)
            params.add('amp', value=YS[-1]-YS[0])
            params.add('gamma_avg', value = 1.0/5e3)
            params.add('gamma_diff', value=1e-7, min=1.0/500e5, vary=False)
            result = lmfit.minimize(two_scale_exp2, params, args=(XS, YS))
            lmfit.report_fit(result.params)
            
#            midpoint = result.params['ofs'] + result.params['amp']/2
#            half_life = -result.params['tau'] * np.log(-1.0/result.params['delay'] * np.log((midpoint - result.params['ofs'])/result.params['amp']))
            fig.axes[0].plot(XS/1e3, -two_scale_exp2(result.params, XS, 0), label='Fit, gamma_avg = %.03f /us +/- %.03f /us \n gamma_diff = %.03f /us +/- %.03f /us'# \n halflife = %.03f us'
                    %(result.params['gamma_avg'].value*1e3, result.params['gamma_avg'].stderr*1e3, result.params['gamma_diff'].value*1e3, result.params['gamma_diff'].stderr*1e3))
            fig.axes[0].legend(loc=0)
            fig.axes[0].set_ylabel('Intensity [AU]')
            fig.axes[0].set_xlabel('Time [us]')
            fig.axes[1].plot(XS/1e3, two_scale_exp2(result.params, XS, YS), marker='s')

        if 0: # two-scale exponential fit deep overdamped
            XS = xs
            params = lmfit.Parameters()
            params.add('ofs', value=0, vary=True)
            params.add('amp', value=YS[-1])
            params.add('gamma1', value = 1.0/5e3)
            params.add('gamma2', value = 1.0/10e3, min=1.0/500e5)
            result = lmfit.minimize(two_scale_exp, params, args=(XS, YS))
            lmfit.report_fit(result.params)
            
#            midpoint = result.params['ofs'] + result.params['amp']/2
#            half_life = -result.params['tau'] * np.log(-1.0/result.params['delay'] * np.log((midpoint - result.params['ofs'])/result.params['amp']))
            fig.axes[0].plot(XS/1e3, -two_scale_exp(result.params, XS, 0), label='Fit, gamma1 = %.03f /us +/- %.03f /us \n gamma2 = %.03f /us +/- %.03f /us'# \n halflife = %.03f us'
                    %(result.params['gamma1'].value*1e3, result.params['gamma1'].stderr*1e3, result.params['gamma2'].value*1e3, result.params['gamma2'].stderr*1e3))
            fig.axes[0].legend(loc=0)
            fig.axes[0].set_ylabel('Intensity [AU]')
            fig.axes[0].set_xlabel('Time [us]')
            fig.axes[1].plot(XS/1e3, two_scale_exp(result.params, XS, YS), marker='s')
                

    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')

    fig.canvas.draw()
    
#    return result.params['gamma_avg'].value
#    return half_life
    return result.params


class poly_time_domain(Measurement1D):

    def __init__(self, comb_list, qubit_list, delays, post_delay = 1e3,
                 seq=None, postseq=None, bgcor=False, skip_points = 1, **kwargs):
        self.comb_list = comb_list
        self.qubit_list = qubit_list
        self.delays = delays
        self.post_delay = post_delay
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
        self.skip_points = skip_points
    
        if bgcor:
            n_rep = len(qubit_list)+1
        else:
            n_rep = len(qubit_list)
        xs_single = self.delays/1e3
        self.xs = np.tile(xs_single, n_rep)
        npoints = len(self.delays) * n_rep
        
        infos = [comb.info for comb in comb_list]
        
        super(poly_time_domain, self).__init__(npoints, infos=infos + qubit_list, **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(delays)])
        self.data.create_dataset('delays', data=self.delays)
        self.data.set_attrs(
#                fwm_amps = comb_list[0].amps,
#                ge_amps = comb_list[1].amps,
#                stark_shift = comb_list[0].stark_shift
        )

    def generate(self):
        s = Sequence()
        
        for info in self.qubit_list:
            r = info.rotate_selective
            
            for dt in self.delays:
                s.append(self.seq)
                if dt > 0:
                    poly_seq = []
                    for comb in self.comb_list:
                        poly_seq += comb.get_poly_seq(dt - comb.sigma*4, 0)
                    if len(poly_seq) == 0:
                        poly_seq += [Delay(dt)]
                    s.append(Combined(poly_seq))
                s.append(Delay(self.post_delay))
                s.append(r(np.pi, X_AXIS))
        
                if self.postseq:
                    s.append(self.postseq)
                s.append(self.readout_driver.do_get_sequence(self.readout_qubit_info))
                s.append(Delay(2000))
                
        if self.bgcor:
            for dt in self.delays:
                s.append(self.seq)
                if dt > 0:
                    poly_seq = []
                    for comb in self.comb_list:
                        poly_seq += comb.get_poly_seq(dt - comb.sigma*4, 0)
                    if len(poly_seq) == 0:
                        poly_seq += [Delay(dt)]
                    s.append(Combined(poly_seq))
                s.append(Delay(self.post_delay))
#                s.append(r(np.pi, X_AXIS))
        
                if self.postseq:
                    s.append(self.postseq)
                s.append(self.readout_driver.do_get_sequence(self.readout_qubit_info))
                s.append(Delay(2000))
                
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)

