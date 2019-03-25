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

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)
    
    return 

class CoilResponse(Measurement1D):

    def __init__(self, qubit_info, delays, double_exp=False, seq=None,
                 postseq=None,laser_power = None, Qswitch_infoB=None, **kwargs):
        self.qubit_info = qubit_info
        self.delays = delays
        self.xs = delays / 1e3      # For plotting purposes
        self.double_exp = double_exp
        self.laser_power = laser_power
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.QswB = Qswitch_infoB

        super(CoilResponse, self).__init__(len(delays), infos=qubit_info, **kwargs)
        self.data.create_dataset('delays', data=delays)
#        self.data.set_attrs(laser_power =self.laser_power)


    def generate(self):
        s = Sequence()
#        s.append(Constant(250, 0, chan=4))
#        s.append(Constant(250, 1, chan='4m1'))
        r = self.qubit_info.rotate
        _w = self.qubit_info.w
        for i, dt in enumerate(self.delays):
            s.append(self.seq)
            s.append(Constant(int(dt), 1, chan=5))
            s.append(Combined([Constant(int(_w*4), 1, chan=5),
                    r(np.pi, 0),
            ]))

            if self.postseq is not None:
                s.append(self.postseq)
#            s.append(self.get_readout_pulse())
            
#            s.append(Delay(20))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=5),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
            s.append(Delay(1000))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
#        return self.fit_params['tau'].value
