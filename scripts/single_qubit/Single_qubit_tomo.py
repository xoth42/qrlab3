import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = np.linspace(0,5,6)

  
    fig.axes[0].plot(xs, ys)

    
    fig.canvas.draw()
    fig.axes[0].legend(loc=0)

    return


class Single_qubit_tomo(Measurement1D):

    def __init__(self, qubit_info, repeat_pulse=1, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.repeat_pulse = repeat_pulse
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        super(Single_qubit_tomo, self).__init__(6, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('direction', data=np.linspace(0,5,6))
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate
        
        '''measure sigma x'''
        s.append(self.seq)
        

        s.append(r(-np.pi/2, Y_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))
        
        '''measure sigma x'''
        s.append(self.seq)
        
        s.append(r(-np.pi/2, Y_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        '''measure sigma y'''
        s.append(self.seq)
       

        s.append(r(np.pi/2, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))
        
        '''measure sigma y'''
        s.append(self.seq)
   

        s.append(r(np.pi/2, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))       
        
        '''measure sigma z'''
        s.append(self.seq)


        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))
        
        '''measure sigma z'''
        s.append(self.seq)


        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))

        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
        return #self.fit_params['tau'].value
