import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


#def analysis(meas, data=None, fig=None):
#    ys, fig = meas.get_ys_fig(data, fig)
##    xs = meas.xs
#
#
#    A = np.array([[1, -1, -1,1], [1,1,-1,-1], [1,-1,1,-1],[1,1,1,1]])
#    B = np.array([ys[0], ys[1], ys[2], ys[3]])
#    beta = np.linalg.solve(A,B)
#    b0 = beta[0]
#    b1 = beta[1]
#    b2 = beta[2]
#    b3 = beta[3]
##
## the order of the matrix elements vector is: ZI, IZ, ZX, ZY, ZZ, YI, IY, 
##YX, YY, YZ, XI, IX, XX, XY, XZ
##        
#    M_vector = np.array([ys[4], ys[5] , ys[6], ys[7], ys[8], ys[9], ys[10], ys[11],
#                    ys[12], ys[13], ys[14], ys[15], ys[16], ys[17], ys[18]])
#
#    M_matrix = np.array([[b1,b2,0,0,b3,0,0,0,0,0,0,0,0,0,0],
#                         [-1*b1,b2,0,0,-1*b3,0,0,0,0,0,0,0,0,0,0],
#                         [b1,-1*b2,0,0,-1*b3,0,0,0,0,0,0,0,0,0,0],
#                         [0,b2,0,0,0,b1,0,0,0,b3,0,0,0,0,0],
#                         [0,0,0,0,0,b1,b2,0,b3,0,0,0,0,0,0],
#                         [0,0,0,0,0,b1,0,-1*b3,0,0,0,-1*b2,0,0,0],
#                         [0,-1*b2,0,0,0,b1,0,0,0,-1*b3,0,0,0,0,0],
#                         [0,b2,0,0,0,0,0,0,0,0,-1*b1,0,0,0,-1*b3],
#                         [0,0,0,0,0,0,b2,0,0,0,-1*b1,0,0,-1*b3,0],
#                         [0,0,0,0,0,-1*b1,-1*b2,b3,0,0,0,0,0,0,0],
#                         [-1*b2,0,0,0,0,0,0,0,0,0,-1*b1,0,0,0,b3],
#                         [b1,0,0,b3,0,0,b2,0,0,0,0,0,0,0,0],
#                         [-1*b1,0,0,-1*b3,0,b2,0,0,0,0,0,0,0,0],
#                         [b1,0,-1*b3,0,0,0,0,0,0,0,0,-1*b2,0,0,0],
#                         [-1*b1,0,b3,0,0,0,0,0,0,0,0,-1*b2,0,0,0]])

#    M_matrix = np.array([[b1,b2,0,0,b3,0,0,0,0,0,0,0,0,0,0],
#                  [-1*b1,b2,0,0,-1*b3,0,0,0,0,0,0,0,0,0,0],
#                  [b1,-1*b2,0,0,-1*b3,0,0,0,0,0,0,0,0,0,0],
#                  [0,b2,0,0,0,b1,0,0,0,b3,0,0,0,0,0],
#                  [0,0,0,0,0,b1,b2,0,b3,0,0,0,0,0,0],
#                  [0,0,0,0,0,b1,0,-1*b3,0,0,0,-1*b2,0,0,0],
#                  [0,-1*b2,0,0,0,b1,0,0,0,-1*b3,0,0,0,0,0],
#                  [0,b2,0,0,0,0,0,0,0,0,-1*b1,0,0,0,-1*b3],
#                  [0,0,0,0,0,0,b2,0,0,0,-1*b1,0,0,-1*b3,0],
#                  [0,0,0,0,0,-1*b1,-1*b2,b3,0,0,0,0,0,0,0],
#                  [-1*b2,0,0,0,0,0,0,0,0,0,-1*b1,0,0,0,b3],
#                  [b1,0,0,b3,0,0,b2,0,0,0,0,0,0,0,0],
#                  [-1*b1,0,0,-1*b3,0,0,b2,0,0,0,0,0,0,0,0],
#                  [b1,0,-1*b3,0,0,0,0,0,0,0,0,-1*b2,0,0,0],
#                  [-1*b1,0,b3,0,0,0,0,0,0,0,0,-1*b2,0,0,0]])
#
#
#    M = np.linalg.solve(M_matrix, M_vector)
#    print(M)              
#
#
#    return M
#
#




class twoqubit_state_tomo(Measurement1D):

    def __init__(self, gate_info1, gate_info2, seq=None, seq_cool=None, postseq=None, **kwargs):
        self.gate_info1 = gate_info1
        self.gate_info2 = gate_info2
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        if seq_cool is None:
            seq_cool = Trigger(250)
        self.seq_cool=seq_cool
        self.postseq = postseq

#        XS= np.append(np.array(range(-4,0)), np.array(range(0,15,15)))                                  
#        self.xs = XS
        

        super(twoqubit_state_tomo, self).__init__(19, infos=(gate_info1,gate_info2), **kwargs)
        self.data.create_dataset('sequence', data=[list(range(0,15))])
        self.data.set_attrs()






    def generate(self):
        s = Sequence()

        r = self.gate_info1.rotate
        r2= self.gate_info2.rotate
        

        '''Vgg, Veg, Vge, Vee measured'''
        
        s.append(self.seq_cool)
        s.append(Delay(24))   #Delay is used instead of identity 
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   

        s.append(self.seq_cool)
        s.append(r(np.pi, X_AXIS))   #Delay is used instead of identity 
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   

        s.append(self.seq_cool)
        s.append(r2(np.pi, X_AXIS))   #Delay is used instead of identity 
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   

        s.append(self.seq_cool)
        s.append(Combined([r(np.pi, X_AXIS), r2(np.pi,X_AXIS)]))   #Delay is used instead of identity 
        s.append(self.postseq)
        s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
        s.append(Delay(2000))   
       


        '''M01'''
        
        s.append(self.seq)
        s.append(Delay(24))   #Delay is used instead of identity 
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
#        M = analysis(self, data, fig)
        return  #self.fit_params['tau'].value
