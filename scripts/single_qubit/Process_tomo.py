import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


class Process_tomo(Measurement1D):

    def __init__(self, qubit_info, seq=None, process_seq=None, **kwargs):
        self.qubit_info = qubit_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.process_seq=process_seq

        super(Process_tomo, self).__init__(9, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('direction', data=[0, 1, 2])
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate

        init_states = [r(-np.pi/2, Y_AXIS), r(np.pi/2, X_AXIS), Delay(80)]
        for init_state in init_states:
            s.append(self.seq)
            s.append(init_state) #prepare x or y or z
            s.append(self.process_seq)
            '''measure sigma x after the process to be characterized'''
            s.append(r(-np.pi/2, Y_AXIS))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                
            s.append(self.seq)
            s.append(init_state) #prepare x or y or z
            s.append(self.process_seq)
            '''measure sigma y after the process to be characterized'''
            s.append(r(np.pi/2, X_AXIS))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            
            s.append(self.seq)
            s.append(init_state) #prepare x or y or z
            s.append(self.process_seq)
            '''measure sigma z after the process to be characterized'''
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))

        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):
#        self.fit_params = analysis(self, data, fig)
        return #self.fit_params['tau'].value
