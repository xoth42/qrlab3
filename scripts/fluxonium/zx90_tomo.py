import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit
def analysis(meas, data=None, fig=None):

    ys, fig = meas.get_ys_fig(data, fig)
    xs = np.linspace(1,5,5)
#    ys = meas.avg_data
    # We now pull complex data to process populations at this point  
    y2d = ys.reshape(len(ys)/4,4)
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    y3s = y2d[:,2]
    y4s = y2d[:,3]    

    #3 is the number of calibration point here
    calibration_qubit1_excited = (y1s[0] + y2s[0] + y3s[0] + y4s[0])/4
    calibration_qubit2_excited = (y1s[1] + y2s[1] + y3s[1] + y4s[1])/4
    calibration_bothqubits_excited = (y1s[2] + y2s[2] + y3s[2] + y4s[2])/4
    calibration_ground = (y1s[3] + y2s[3] + y3s[3] + y4s[3])/4
    Veg = np.mean(calibration_qubit1_excited)
    Vge = np.mean(calibration_qubit2_excited)
    Vee = np.mean(calibration_bothqubits_excited)
    Vgg = np.mean(calibration_ground)
    print(Veg, Vge, Vee, Vgg)

    plt.figure()   
    plt.plot(xs, y1s, 'bs', ms=3, color='r', linestyle = '-', label='none')
    plt.plot(xs, y2s, 'rs', ms=3, color = 'b', linestyle = '-', label= 'pi pulse on 1')    
    plt.plot(xs, y3s, 'bs', ms=3, color= 'g', linestyle = '-', label = 'pi pulse on 2')
    plt.plot(xs, y4s, 'rs', ms=3, color='y', linestyle = '-', label = 'pi pulse on both')    
#
#    fig.axes[0].legend()
#    fig.canvas.draw()
#
#
##    
###    
###    q1_epop_cplx = ((y1s[13:] + y3s[13:]) - (Vge + Vgg))/ (Veg-Vgg+Vee-Vge)
###    
###    fig2, axes2 = plt.subplots(2)
###    axes2[0].plot(xs[13:], np.real(q1_epop_cplx))
###    axes2[1].plot(xs[13:], np.imag(q1_epop_cplx))
####
###    return q1_epop_cplx
###
###
### ge~ -10, eg~ +8, ee~ +6
###
####
##
##    rd = y1s[12:]
##    bl = y2s[12:]
##    gr = y3s[12:]
##    yw = y4s[12:]
##    Pg1 = ((-rd-gr+bl+yw)/(Veg-Vgg+Vee-Vge)+1)/2
##    Pg2 = ((-rd-bl+gr+yw)/(Vge-Vgg+Vee-Veg)+1)/2
#    
    B = ((y1s[4:] + y3s[4:]) - (Vge + Vgg))/ (Veg-Vgg+Vee-Vge)  #QUBIT 1 POPULATION (P2 +P3)
    D = ((y1s[4:] + y2s[4:]) - (Veg + Vgg))/ (Vge-Veg-Vgg+Vee)   #QUBIT 2 POPULATION (P1 +P3)
    C = ((y2s[4:] + y3s[4:]) - (Vge + Veg)) / (Vee-Vge-Veg + Vgg)  #(P1 + P2)
    A = ((y1s[4:] + y4s[4:]) - (Vge + Veg)) / (Vee - Vge - Veg + Vgg)  # (P0 + P3)
##    Pg_cplx = A-((D-C+B)/2)
##
##    Pegge = ((rd+yw-bl-gr)/(Vge+Veg-Vee-Vgg)+1)/2
##    Pg_cplx = (Pg1+Pg2-Pegge)/2
##    
    P0 = A - B + (C/2)
    P1 = (C/2) - B + D
    P2 = (B - D + C)/2
    P3 = B - (C/2)


    print(P0)
    print(P1)
    print(P2)
    print(P3)
    #
#
#    fig2, axes2 = plt.subplots(2)
#    axes2[0].plot(xs[12:], np.real(P0), color = 'b')
#    axes2[0].plot(xs[12:], np.real(P1), color='r')
#    axes2[0].plot(xs[12:], np.real(P2), color = 'g')
#    axes2[0].plot(xs[12:], np.real(P3), color = 'o')
    
    return  [P0,P1,P2,P3]

class zx90_tomo(Measurement1D):

    def __init__(self, control_info, target_info, zx90_info, seq=None, postseq=None, **kwargs):
        self.control_info = control_info
        self.target_info = target_info
        self.zx90_info = zx90_info
        self.seq=seq
        self.postseq=postseq
        super(zx90_tomo, self).__init__(20, infos=(control_info, target_info, zx90_info,), **kwargs)
        self.data.create_dataset('sequence', data=[list(range(0,20))])


    def generate(self):
        s = Sequence()

        c = self.control_info.rotate
        zx90 = self.zx90_info.rotate
        t = self.target_info.rotate
#
        for j in range(1):
#            s.append(self.seq)      #Ebru: take this out after making sure that it causes no problem

            temp_seq = Sequence()
            temp_seq.append(c(np.pi,0))   
            for i in range(4):


                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses qubit 1')


        for j in range(1):
#            s.append(self.seq)

            temp_seq = Sequence()
            temp_seq.append(t(np.pi,0))   
            for i in range(4):


                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses qubit 2')


        for j in range(1):
            s.append(self.seq) 

            temp_seq = Sequence()
            temp_seq.append(Combined([t(np.pi,0),c(np.pi,0)]))   
            for i in range(4):


                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses for both qubits')

        
        
        for j in range(1):

            temp_seq = Sequence()
#            s.append(Delay(24))   
            for i in range(4):
                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration ground state')


#        for initial_state in ['00', '10', '01', '11']: #first one is control, second one is target
#            if initial_state == '10':
#                s.append(c(np.pi,0))
#            if initial_state == '01':
#                s.append(t(np.pi,0))
#            if initial_state == '11':
#                s.append(Combined([c(np.pi,0),t(np.pi,0)]))
#
#This is our ZX90 package
                
        
#            if self.postseq:
#                s.append(self.postseq)


        for ROpostseq in [None, t(np.pi,0), c(np.pi,0), Combined([c(np.pi,0),t(np.pi,0)])]:
            
            s.append(self.seq)
#            s.append(t(np.pi,0))
            s.append(self.zx90_info.rotate(-np.pi,0))
            s.append(c(np.pi,0))
            s.append(self.zx90_info.rotate(np.pi,0))
            s.append(c(np.pi,0))
            s.append(ROpostseq)
            s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
    
    
#    
#            s.append(Delay(1000))
#
        s = self.get_sequencer(s)
        seqs = s.render()
        self.seqs = seqs
        return seqs

    def analyze(self, data=None, fig=None):
        self.pg = analysis(self, data, fig)
        return #self.fit_params['tau'].value
#    def analyze(self, data, fig):
##        self.Pg_cplx = analysis(self, data, fig)
#        return self.Pg_cplx
