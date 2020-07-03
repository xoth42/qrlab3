import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


class Two_qubit_tomo(Measurement1D):

    def __init__(self, qubit_info, qubit_info2, qubit2_info, qubit2_info2, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.qubit_info2 = qubit_info2
        self.qubit2_info = qubit2_info
        self.qubit2_info2 = qubit2_info2
        
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        super(Two_qubit_tomo, self).__init__(80, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('direction', data=np.linspace(0,79,80))
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate
        r2 = self.qubit_info2.rotate
        R = self.qubit2_info.rotate
        R2 = self.qubit2_info2.rotate

        '''measure sigma XI'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(-np.pi/2, Y_AXIS), r2(-np.pi/2,Y_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 
        
        
        
            
        '''measure sigma YI'''
        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(np.pi/2, X_AXIS), r2(np.pi/2,X_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 
        
        '''measure sigma ZI NOT CORRECT'''  #SKIPPED THAT FOR THE MOMENT
        for i in range(5):
            s.append(self.seq)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
    
    
        '''measure sigma IX'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([R(-np.pi/2, Y_AXIS), R2(-np.pi/2,Y_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 
        
        
        
            
        '''measure sigma IY'''
        for i in range(5):

            s.append(self.seq)
            s.append(Combined([R(np.pi/2, X_AXIS), R2(np.pi/2,X_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 
        
        '''measure sigma IZ NOT CORRECT'''  #SKIPPED THAT FOR THE MOMENT
        s.append(self.seq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        '''measure sigma XX'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(-np.pi/2, Y_AXIS), r2(-np.pi/2,Y_AXIS), R(-np.pi/2, Y_AXIS), R2(-np.pi/2, Y_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 
        
        

        '''measure sigma XY'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(-np.pi/2, Y_AXIS), r2(-np.pi/2,Y_AXIS), R(np.pi/2, X_AXIS), R2(np.pi/2, X_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 


        '''measure sigma XZ not correct!!!!!!!!!!!'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(-np.pi/2, Y_AXIS), r2(-np.pi/2,Y_AXIS), R(np.pi/2, X_AXIS), R2(np.pi/2, X_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 


        '''measure sigma YY'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(np.pi/2, X_AXIS), r2(np.pi/2,X_AXIS), R(np.pi/2, X_AXIS), R2(np.pi/2, X_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 
        
        

        '''measure sigma YX'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(np.pi/2, X_AXIS), r2(np.pi/2,X_AXIS), R(-np.pi/2, Y_AXIS), R2(-np.pi/2, Y_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 


        '''measure sigma YZ not correct!!!!!!!!!!!'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(-np.pi/2, Y_AXIS), r2(-np.pi/2,Y_AXIS), R(np.pi/2, X_AXIS), R2(np.pi/2, X_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 

        '''measure sigma ZX NOT CORRECT'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(-np.pi/2, Y_AXIS), r2(-np.pi/2,Y_AXIS), R(-np.pi/2, Y_AXIS), R2(-np.pi/2, Y_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 
        
        

        '''measure sigma ZY NOT CORRECT'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(-np.pi/2, Y_AXIS), r2(-np.pi/2,Y_AXIS), R(np.pi/2, X_AXIS), R2(np.pi/2, X_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 


        '''measure sigma ZZ not correct!!!!!!!!!!!'''

        for i in range(5):

            s.append(self.seq)
            s.append(Combined([r(-np.pi/2, Y_AXIS), r2(-np.pi/2,Y_AXIS), R(np.pi/2, X_AXIS), R2(np.pi/2, X_AXIS)]))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(20000)) 

        '''measure II'''

        for i in range(5):
            s.append(self.seq)
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
