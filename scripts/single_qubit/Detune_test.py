import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import matplotlib.pyplot as plt
import copy
import mclient
import lmfit

center_amp_list =[] #Ebru

def linear_fit(params, x, data):
    est = params['m']*x + params['n']
    return (data-est)

def linear_fit2(params, x):
    est = params['m']*x + params['n']
    return est

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.xs
#    ys = meas.get_ys()
    ys1, ys2 = np.split(ys,2)      #Splitting the measurement result in two to fit them separately
    xs1, xs2 = np.split(xs,2)
    
    params = lmfit.Parameters()
    params.add('m', value=0)
    params.add('n', value=0)
    result1 = lmfit.minimize(linear_fit, params, args=(xs1,ys1))
    result2 = lmfit.minimize(linear_fit, params, args=(xs2,ys2))
    
    lmfit.report_fit(result1.params)
    lmfit.report_fit(result2.params)
    plt.figure()
    plt.plot(xs1, linear_fit2(result1.params, xs1), color='r')
    plt.plot(xs2, linear_fit2(result2.params, xs2), color='b')
    plt.plot(xs1, ys1, color='r')
    plt.plot(xs2, ys2, color='b')


class Detune_test(Measurement1D):

    def __init__(self, qubit_info, amps, update=False, seq=None, r_axis=0,
                 repeat_pulse=1, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.amps = amps
        self.xs = np.concatenate((amps,amps))
        self.update_ins = update
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis
        
        super(Detune_test, self).__init__(len(amps)*2, infos=qubit_info, **kwargs)
        self.data.create_dataset('amps', data=amps)

    def generate(self):  #That is the original generate function 
        s = Sequence()

        for i, amp in enumerate(self.amps):
            s.append(self.seq)
            s.append(self.qubit_info.rotate(np.pi/2, 0))

            g = DetunedSum(self.qubit_info.base, self.qubit_info.w, chans=self.qubit_info.sideband_channels)
            if df != 0:
                period = 1e9 / df
            else:
                period = 1e50
            g.add(self.qubit_info.pi_amp, period)
            s.append(g())

            s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=amp), self.repeat_pulse))
            if self.postseq is not None:
                s.append(self.postseq)
            s.append(Delay(20))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000))

        for i, amp in enumerate(self.amps):
            s.append(self.seq)
            s.append(self.qubit_info.rotate(np.pi/2, 0))
            s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=-amp), self.repeat_pulse))
            if self.postseq is not None:
                s.append(self.postseq)
            s.append(Delay(20))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

#    def generate(self): #Ebru: I am playing with this one
#        s = Sequence()
#        s.append(Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan))  #acquisition
#        for i, amp in enumerate(self.amps):
#            s.append(self.seq)           
#            if self.selective==1:
#                s.append(Repeat(self.qubit_info.rotate_selective(0, self.r_axis, amp=amp), self.repeat_pulse))
#            elif self.selective==0.5:
#                s.append(Repeat(self.qubit_info.rotate_quasilective(0, self.r_axis, amp=amp), self.repeat_pulse))
#            else:
#                s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=amp), self.repeat_pulse))
#            if self.postseq is not None:
#                s.append(self.postseq)
#            s.append(Delay(200))
#            s.append(Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan))
#            s.append(Delay(2000))
#
#
#
#        s = self.get_sequencer(s)
#        seqs = s.render()
#        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return #self.fit_params['tau'].value    


    ''' JEFF. Used to populate data in measuremnt from hdf5 file instead of a measurement for analysis. '''
    def load_data(self, filepath, exp_path):
        return 0
        
        