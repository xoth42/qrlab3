import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


class All_XY_interleaved(Measurement1D):

    def __init__(self, qubit_info, qubit_info2, qubit2_info, rel_amp, rel_angle, qubit2_rotation=0, qubit2_angle = np.pi, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.qubit_info2 = qubit_info2
        self.qubit2_info = qubit2_info
        self.rel_amp = rel_amp
        self.rel_angle = rel_angle
        self.qubit2_rotation = qubit2_rotation
        self.qubit2_angle = qubit2_angle
        
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        super(All_XY_interleaved, self).__init__(42, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('sequence', data=[range(0,42)])
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()

#        self.qubit2_angle = np.pi
#        self.qubit2_rotation = 0            
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        wait = Delay(5)

        '''North pole sequences'''
        s.append(self.seq)
        
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))  
        
        

        s.append(self.seq)
        
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))





        
        s.append(self.seq)
        
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
       
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))        
        
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))

        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
       
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  
        
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
       
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))  
                        
    
        s.append(self.seq)
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 


    
        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 



        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        
        
        
        
        '''Equator sequences'''
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        

        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 




        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 




        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 




        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 




        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 



        s.append(self.seq)
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 


        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 


        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        s.append(self.seq)
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        '''South pole sequences'''
        s.append(self.seq)
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 


        s.append(self.seq)
        s.append(Combined([r(np.pi,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        s.append(self.seq)
        s.append(Combined([r(np.pi,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        s.append(self.seq)
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,X_AXIS), self.qubit_info2.rotate(0, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 
        
        
        
        
        
        
        
        
        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        s.append(self.seq)
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(self.qubit2_angle,self.qubit2_rotation))        
        s.append(Combined([r(np.pi/2,Y_AXIS), self.qubit_info2.rotate(1, self.rel_angle/2, amp=self.qubit_info.pi_amp*self.rel_amp)]))
        s.append(r2(-1*self.qubit2_angle,self.qubit2_rotation))
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
