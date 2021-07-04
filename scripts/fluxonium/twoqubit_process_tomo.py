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




class twoqubit_process_tomo(Measurement1D):

    def __init__(self, gate_info1, gate_info2, ZZ_info, seq=None, seq_cool=None, postseq=None, **kwargs):
        self.gate_info1 = gate_info1
        self.gate_info2 = gate_info2
        self.ZZ_info = ZZ_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        if seq_cool is None:
            seq_cool = Trigger(250)
        self.seq_cool=seq_cool
        self.postseq = postseq

#        XS= np.append(np.array(range(-4,0)), np.array(range(0,15,15)))                                  
#        self.xs = XS
        

        super(twoqubit_process_tomo, self).__init__(229, infos=(gate_info1,gate_info2, ZZ_info), **kwargs)
        self.data.create_dataset('sequence', data=[list(range(0,229))])
        self.data.set_attrs()






    def generate(self):
        s = Sequence()

        r = self.gate_info1.rotate
        r2= self.gate_info2.rotate
        ZZ = self.ZZ_info.rotate        

        '''Vgg, Veg, Vge, Vee measured'''
        rot_list = [Delay(24), r(np.pi, X_AXIS), r2(np.pi, X_AXIS),r(np.pi/2, X_AXIS),
                    Combined([r(np.pi/2, X_AXIS), r2(np.pi/2, X_AXIS)]), Combined([r(np.pi/2, X_AXIS), r2(np.pi/2, Y_AXIS)]),
                    Combined([r(np.pi/2, X_AXIS), r2(np.pi, Y_AXIS)]), r(np.pi/2, Y_AXIS), Combined([r(np.pi/2, Y_AXIS), r2(np.pi/2, X_AXIS)]),
                     Combined([r(np.pi/2, Y_AXIS), r2(np.pi/2, Y_AXIS)]), Combined([r(np.pi/2, Y_AXIS), r2(np.pi, X_AXIS)]),
                     r2(np.pi/2, X_AXIS), Combined([r(np.pi, X_AXIS), r2(np.pi/2, X_AXIS)]),
                     r2(np.pi/2, Y_AXIS), Combined([r(np.pi, X_AXIS), r2(np.pi/2, Y_AXIS)])]                    
#
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
       


#        '''M01'''
#        
#        s.append(self.seq)
#        s.append(Delay(24))   #Delay is used instead of identity 
#        s.append(self.postseq)
#        s.append(Combined([
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#            ]))
#        s.append(Delay(2000))   
#

        for i in rot_list:
            for j in rot_list:
                s.append(self.seq)
                s.append(rot_list[i])  
                s.append(ZZ(np.pi,0))
                s.append(rot_list[j])
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
