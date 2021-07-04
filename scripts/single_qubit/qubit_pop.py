import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


#array = np.array([1.4571449, -3.5474763, 2.850724, -0.6950667, -5.04537])
#
#print()

#sols = np.array([3.96, -5.52,  4.37,  -1.15, -5.63])
#
#from scipy.optimize import fsolve
#import math
#
#
#p0 = 0.94
#p1 = 0.04
#p2 = 1 - p0 - p1
#
#phi_g = 4.5
#phi_e = -5.7
#phi_f = -1.5
#
#print(np.array([p0*phi_g + p1*phi_e + p2*phi_f,
#p1*phi_g + p0*phi_e + p2*phi_f,
#p0*phi_g + p2*phi_e + p1*phi_f,
#p1*phi_g + p2*phi_e + p0*phi_f,
#p2*phi_g + p0*phi_e + p1*phi_f]))
#
#
#def equations(p):
#    p0, p1, phi_g, phi_e, phi_f = p
#    return (p0*phi_g + p1*phi_e + (1.0-p0-p1)*phi_f - sols[0],
#            p1*phi_g + p0*phi_e + (1.0-p0-p1)*phi_f - sols[1],
#            p0*phi_g + (1.0-p0-p1)*phi_e + p1*phi_f - sols[2],
#            p1*phi_g + (1.0-p0-p1)*phi_e + p0*phi_f - sols[3],
#            (1.0-p0-p1)*phi_g + p0*phi_e + p1*phi_f - sols[4])
#    
#p0, p1, phi_g, phi_e, phi_f = fsolve(equations, (0.9, 0.05, sols[0], sols[1], sols[3]))

#print (equations(p))


class Qubit_Pop(Measurement1D):

    def __init__(self, qubit_info, ef_info, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.ef_info = ef_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        super(Qubit_Pop, self).__init__(14, infos=(qubit_info, ef_info), **kwargs)
        self.data.create_dataset('sequence', data=[list(range(0,14))])
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()


        r = self.qubit_info.rotate
        r_ef = self.ef_info.rotate

        '''Identity sequence'''
        s.append(self.seq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   
        
        s.append(self.seq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

 


        '''0-1 0-1'''
        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))
        s.append(r(np.pi, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   
        
        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))
        s.append(r(np.pi, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 


        
        '''0-1 Pi pulse'''
        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 

        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))



        
        '''1-2 Pi pulse'''
        s.append(self.seq)
        s.append(r_ef(np.pi, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))        

        s.append(self.seq)
        s.append(r_ef(np.pi, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000)) 


        s.append(Delay(2000))         
        '''0-1, 1-2 Pi Pulse'''
        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))
        s.append(r_ef(np.pi, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))

        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))
        s.append(r_ef(np.pi, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))

   
        '''1-2, 0-1 Pi Pulse'''
        s.append(self.seq)
        s.append(r_ef(np.pi, X_AXIS))
        s.append(r(np.pi, X_AXIS))
        
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))
        
        s.append(self.seq)
        s.append(r_ef(np.pi, X_AXIS))
        s.append(r(np.pi, X_AXIS))
        
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))
       
        '''0-1,1-2,0-1 Pulse'''
        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))
        s.append(r_ef(np.pi, X_AXIS))
        s.append(r(np.pi, X_AXIS))
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ])) 
        s.append(Delay(2000))

        s.append(self.seq)
        s.append(r(np.pi, X_AXIS))
        s.append(r_ef(np.pi, X_AXIS))
        s.append(r(np.pi, X_AXIS))
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
