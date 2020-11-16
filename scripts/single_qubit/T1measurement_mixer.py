import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import h5py
import lmfit

def exp_decay(params, x, data):
    est = params['ofs'] + params['amplitude'] * np.exp(-x / params['tau'].value)
    return data - est

def double_exp_decay(params, x, data):
    est = params['ofs'].value + params['amplitude'].value * np.exp(-x / params['tau'].value) + params['amplitude2'].value * np.exp(-x / params['tau2'].value)
    return data - est


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.delays

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3, linestyle='-', markerfacecolor='red' )
    fig.axes[0].errorbar(xs/1e3, ys, yerr=meas.get_stes(), fmt='.', 
                         markersize = 0, ecolor='grey', linewidth=1)

    if meas.double_exp == False:
        params = lmfit.Parameters()
        params.add('ofs', value=np.min(ys))
        params.add('amplitude', value=np.max(ys))
        params.add('tau', value=xs[-1]/2.0, min=50.0)
        result = lmfit.minimize(exp_decay, params, args=(xs, ys))
#        lmfit.report_fit(params)
#        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
        lmfit.report_fit(result.params)
       
        fig.axes[0].plot(xs/1e3, -exp_decay(result.params, xs, 0), label='Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
        fig.axes[0].legend(loc=0)
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Time [us]')
        fig.axes[1].plot(xs, exp_decay(result.params, xs, ys), marker='s')




    else:
        params = lmfit.Parameters()
        params.add('ofs', value=np.min(ys))
        params.add('amplitude', value=np.max(ys)/2.0)
        params.add('tau', value=xs[-1]/2.0, min=50.0)  #Chen, fine tune the initial guess a bit 4/27/19
        params.add('amplitude2', value=np.max(ys)/2.0)
        params.add('tau2', value=xs[-1]/50.0, min=50.0)  ##Chen, fine tune the initial guess a bit 4/27/19
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

class T1Measurement_mixer(Measurement1D):

    def __init__(self, qubit_info, mixer_info1, mixer_info2, delays, double_exp=False, seq=None,
                 postseq=None,laser_power = None, Qswitch_infoB=None, **kwargs):
        self.qubit_info = qubit_info
        self.mixer_info1 = mixer_info1
        self.mixer_info2 = mixer_info2
        self.delays = delays
        self.xs = delays / 1e3      # For plotting purposes
        self.double_exp = double_exp
        self.laser_power = laser_power
        if seq is None:
            seq = [Trigger(250)]
        self.seq = seq
        self.postseq = postseq
        self.QswB = Qswitch_infoB

        super(T1Measurement_mixer, self).__init__(len(delays), infos=(qubit_info, mixer_info1, mixer_info2), **kwargs)
        self.data.create_dataset('delays', data=delays)
#        self.data.set_attrs(laser_power =self.laser_power)


    def generate(self):
        s = Sequence()
#        s.append(Constant(250, 0, chan=4))
#        s.append(Constant(250, 1, chan='4m1'))
        if self.mixer_info1.deltaf == 0:
            ro = [Combined([
                Join([Delay(200),Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]),
    #            Join([Constant(self.readout_info.pulse_len + 100, 1, chan=self.readout_info.readout_chan),Delay(200)]),
                Join([Constant(int(self.mixer_info1.w),self.mixer_info1.pi_amp,chan = self.mixer_info1.sideband_channels[0]),Delay(200)]),
                Join([Constant(int(self.mixer_info2.w),self.mixer_info2.pi_amp,chan = self.mixer_info2.sideband_channels[0]),Delay(200)])
    #                Join([Delay(100),Constant(self.readout_info.pulse_len, self.mixer_info.pi_amp, chan=self.mixer_info.channels[0]),Delay(200)]),
            ])]
        else:
            ro = [Combined([
                Join([Delay(200),Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]),
    #            Join([Constant(self.readout_info.pulse_len + 100, 1, chan=self.readout_info.readout_chan),Delay(200)]),
                Join([self.mixer_info1.rotate(np.pi, 0),Delay(200)]),
                Join([self.mixer_info2.rotate(np.pi, 0),Delay(200)])
    #                Join([Delay(100),Constant(self.readout_info.pulse_len, self.mixer_info.pi_amp, chan=self.mixer_info.channels[0]),Delay(200)]),
            ])]       
        
        r = self.qubit_info.rotate
        for i, dt in enumerate(self.delays):
#            s.append(self.seq)
#            s.append(r(np.pi, 0))
##            s.append(Combined([
##                    Constant(25000, 0.1, chan=self.qubit_info.sideband_channels[0]),
##                    Constant(25000, 0.1, chan=self.qubit_info.sideband_channels[1]),
##            ]))
#            if dt > 0:  
#                s.append(Delay(dt))
#
#            if self.postseq is not None:
#                s.append(self.postseq)
#
#            s.append(ro)
#            s.append(Delay(2000))
            #Ebru: changed the delay from 1000 to 20000.
            s_temp = self.seq[:]
            s_temp += [r(np.pi,0)]
            if dt >0:
                s_temp += [Delay(dt)]
            
            if self.postseq:
                s_temp += [self.postseq]
                
            s_temp += ro
            s_temp += [Delay(2000)]
            s.append(Join(s_temp))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return self.fit_params['tau'].value
