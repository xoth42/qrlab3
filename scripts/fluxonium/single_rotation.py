import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


class Single_Rotation(Measurement1D):

    def __init__(self, qubit_info, qubit_info2, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.qubit_info2 = qubit_info2
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        super(Single_Rotation, self).__init__(20, infos=(qubit_info,qubit_info2), **kwargs)
        self.data.create_dataset('sequence', data=[range(0,20)])
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()



#        chs = self.qubit_info.sideband_channels
#        chs2= self.qubit_info2.sideband_channels
        

#        s.append(Combined([Constant(350000, 0.3, chan=chs[0]), Constant(350000, 0.3, chan=chs2[0])]))
#        s.append(Constant(35000, 0.8, chan=chs2[0]))
#        
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))        
##        
        
        r = self.qubit_info.rotate
        r2 = self.qubit_info2.rotate

        wait = Delay(100)

        #|OO> state
        
        
        s.append(self.seq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000)) 

        s.append(self.seq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))         

        s.append(self.seq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))         
        
        s.append(self.seq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000)) 
        
        s.append(self.seq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))           



#|00> to |10>

        s.append(self.seq)
        s.append(r(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000)) 

        s.append(self.seq)
        s.append(r(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))         

        s.append(self.seq)
        s.append(r(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))         
        
        s.append(self.seq)
        s.append(r(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000)) 
        
        s.append(self.seq)
        s.append(r(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))  




#|01> to |11>

        s.append(self.seq)
        s.append(r2(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000)) 

        s.append(self.seq)
        s.append(r2(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))         

        s.append(self.seq)
        s.append(r2(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))         
        
        s.append(self.seq)
        s.append(r2(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000)) 
        
        s.append(self.seq)
        s.append(r2(np.pi,0))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))  





        #Single qubit pulse
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi, 0),r2(np.pi,0)]))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000)) 

        s.append(self.seq)
        s.append(Combined([r(np.pi, 0),r2(np.pi,0)]))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))         

        s.append(self.seq)
        s.append(Combined([r(np.pi, 0),r2(np.pi,0)]))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))         
        
        s.append(self.seq)
        s.append(Combined([r(np.pi, 0),r2(np.pi,0)]))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000)) 
        
        s.append(self.seq)
        s.append(Combined([r(np.pi, 0),r2(np.pi,0)]))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(20000))   
        
        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):
#        self.fit_params = analysis(self, data, fig)
        return #self.fit_params['tau'].value
