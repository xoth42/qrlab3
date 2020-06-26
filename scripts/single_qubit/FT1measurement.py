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

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.delays

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)

    params = lmfit.Parameters()
    params.add('ofs', value=np.min(ys))
    params.add('amplitude', value=np.max(ys)-np.min(ys))
    params.add('tau', value=len(xs)*1000/4.0, min=0)
    result = lmfit.minimize(exp_decay, params, args=(xs, ys))
    lmfit.report_fit(result.params)

    fig.axes[0].plot(xs/1e3, -exp_decay(result.params, xs, 0), label='Fit, tau = %.03f us +/- %.03f us'%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')

    fig.axes[1].plot(xs, exp_decay(result.params, xs, ys), marker='s')
    fig.canvas.draw()
    return result.params

class FT1Measurement(Measurement1D):

    def __init__(self, ge_info, ef_info, delays, seq=None, **kwargs):
        self.ge_info = ge_info
        self.ef_info = ef_info
        self.delays = delays
        self.xs = delays / 1e3      # For plotting purposes

        super(FT1Measurement, self).__init__(len(delays), infos=(ge_info, ef_info), **kwargs)
        self.data.create_dataset('delays', data=delays)
        if seq is None:             #Ebru:Added the seq part for cooling
            seq = Trigger(250)
        self.seq = seq        

    def generate(self):
        s = Sequence()

        r = self.ge_info.rotate
        r_ef = self.ef_info.rotate
        for i, dt in enumerate(self.delays):
            s.append(Join([
                self.seq,   #Ebru: Changed Trigger(dt=250) to self.seq for cooling
                r(np.pi, 0),
                r_ef(np.pi, 0),
            ]))
            if dt > 0:
                s.append(Delay(dt))
#            s.append(r(np.pi/2, 0))
            # For Al better to do ef-pi, ge-pi to get contrast
#            s.append(r_ef(np.pi,0))
#            s.append(r(np.pi,0))
#            s.append(r_ef(np.pi/2,0)) #fluxonium
            s.append(self.get_readout_pulse())
            s.append(Delay(1000))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return self.fit_params['tau'].value
