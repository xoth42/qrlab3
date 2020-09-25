import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


class twoqubit_state_tomo(Measurement1D):

    def __init__(self, gate_info1, gate_info2, seq=None, postseq=None, **kwargs):
        self.gate_info1 = gate_info1
        self.gate_info2 = gate_info2
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        XS= np.append(np.array(range(-4,0)), np.array(range(0,15,15)))                                  
        self.xs = XS


        super(twoqubit_state_tomo, self).__init__(19, infos=(gate_info1,gate_info2), **kwargs)
        self.data.create_dataset('sequence', data=[range(0,15)])
        self.data.set_attrs()






    def generate(self):
        s = Sequence()

        r = self.gate_info1.rotate
        r2= self.gate_info2.rotate
        

        '''Vgg, Veg, Vge, Vee measured'''
        
        s.append(self.seq)
        s.append(delay(24))   #Delay is used instead of identity 
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   

        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))   #Delay is used instead of identity 
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   

        s.append(self.seq)
        s.append(r2(np.pi, X_AXIS))   #Delay is used instead of identity 
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   

        s.append(self.seq)
        s.append(Combined([r(np.pi, X_AXIS), r2(np.pi,X_AXIS)]))   #Delay is used instead of identity 
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   
       


        '''M01'''
        
        s.append(self.seq)
        s.append(delay(24))   #Delay is used instead of identity 
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   

        '''M02'''
        
        s.append(self.seq)
        s.append(r(np.pi,X_AXIS))
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))
        
        '''M03'''
        
        
        s.append(self.seq)
        s.append(r2(np.pi, X_AXIS))
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        '''M04'''
        
        s.append(self.seq)
        s.append(r(np.pi/2, X_AXIS))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))        
        
        '''M05'''
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2, X_AXIS), r2(np.pi/2, X_AXIS)]))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  

        '''M06'''
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2, X_AXIS), r2(np.pi/2, Y_AXIS)]))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  


        '''M07'''
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2, X_AXIS), r2(np.pi, Y_AXIS)]))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  


        '''M08'''
        
        s.append(self.seq)
        s.append(r(np.pi/2, Y_AXIS))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  
        
        '''M09'''
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2, Y_AXIS), r2(np.pi/2, X_AXIS)]))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  
        

        '''M10'''
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2, Y_AXIS), r2(np.pi/2, Y_AXIS)]))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  


        '''M11'''
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2, Y_AXIS), r2(np.pi, X_AXIS)]))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  


        '''M12'''
        
        s.append(self.seq)
        s.append(r2(np.pi/2, X_AXIS))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  


        '''M13'''
        
        s.append(self.seq)
        s.append(Combined([r(np.pi, X_AXIS), r2(np.pi/2, X_AXIS)]))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  


        '''M14'''
        
        s.append(self.seq)
        s.append(r2(np.pi/2, Y_AXIS))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  


        '''M15'''
        
        s.append(self.seq)
        s.append(Combined([r(np.pi, X_AXIS), r2(np.pi/2, Y_AXIS)]))
        s.append(self.postseq)

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  





        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):
#        self.fit_params = analysis(self, data, fig)
        return #self.fit_params['tau'].value
