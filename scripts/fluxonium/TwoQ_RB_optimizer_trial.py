#!/usr/bin/env python3

import random as rnd

#import cliffords

#log = logging.getLogger('LabberDriver')
import os
path_currentdir  = os.path.dirname(os.path.realpath(__file__)) # curret directory

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import math
import random 
import time
import lmfit
import pickle


def exp_decay(params, x, data):
    est = params['A'] * params['alpha']**x + params['B']
    return data - est

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = np.zeros(len(meas.xs)/4)
    for i in range(len(meas.xs)/4):
        xs[i] = meas.xs[4*i]
    
    y2d = ys.reshape(len(ys)/4,4)
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    y3s = y2d[:,2]
    y4s = y2d[:,3]
    
    params = lmfit.Parameters()
    params.add('B', value=np.min(ys))
    params.add('A', value = np.max(ys))
    params.add('alpha', value=xs[-1]/2.0)
#    result = lmfit.minimize(exp_decay, params, args=(xs, ys))
#    lmfit.report_fit(result.params)
    
#    fig.axes[0].plot(xs, -exp_decay(result.params, xs, 0), label='Fit, alpha = %.03f us +/- %.03f us '%(result.params['alpha'].value, result.params['alpha'].stderr))
    fig.axes[0].clear()
    fig.axes[0].plot(xs, y1s, 'bs', ms=3, color='r', linestyle = '-', label='none')
    fig.axes[0].plot(xs, y2s, 'rs', ms=3, color = 'b', linestyle = '-', label= 'pi pulse on 1')    
    fig.axes[0].plot(xs, y3s, 'bs', ms=3, color= 'g', linestyle = '-', label = 'pi pulse on 2')
    fig.axes[0].plot(xs, y4s, 'rs', ms=3, color='y', linestyle = '-', label = 'pi pulse on both')  
    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Phase [AU]')
    fig.axes[0].set_xlabel('# of Cliffords')
    fig.canvas.draw()
    
    ys = meas.avg_data   # We now pull complex data to process populations at this point  
    y2d = ys.reshape(len(ys)/4,4)
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    y3s = y2d[:,2]
    y4s = y2d[:,3]    

    #3 is the number of calibration point here
    calibration_qubit1_excited = (y1s[:3] + y2s[:3] + y3s[:3] + y4s[:3])/4
    calibration_qubit2_excited = (y1s[3:6] + y2s[3:6] + y3s[3:6] + y4s[3:6])/4
    calibration_bothqubits_excited = (y1s[6:9] + y2s[6:9] + y3s[6:9] + y4s[6:9])/4
    calibration_ground = (y1s[9:12] + y2s[9:12] + y3s[9:12] + y4s[9:12])/4
    Veg = np.mean(calibration_qubit1_excited)
    Vge = np.mean(calibration_qubit2_excited)
    Vee = np.mean(calibration_bothqubits_excited)
    Vgg = np.mean(calibration_ground)
    print Veg, Vge, Vee, Vgg

    rd = y1s[12:]
    bl = y2s[12:]
    gr = y3s[12:]
    yw = y4s[12:]


#the original part    
#    Pg1 = ((-rd-gr+bl+yw)/(Veg-Vgg+Vee-Vge)+1)/2
#    Pg2 = ((-rd-bl+gr+yw)/(Vge-Vgg+Vee-Veg)+1)/2
#
#    Pegge = ((rd+yw-bl-gr)/(Vge+Veg-Vee-Vgg)+1)/2
#    Pgg = (Pg1+Pg2-Pegge)/2
#    Pg_cplx = (Pg1+Pg2-Pegge)/2
#
#    
#    fig2, axes2 = plt.subplots(2)
#    axes2[0].plot(xs[12:], np.real(Pgg))
#    axes2[0].plot(xs[12:], np.real(Pg1*Pg2), color='r')
#    axes2[1].plot(xs[12:], np.imag(Pgg))
#    
#    return [Pgg, Pg1, Pg2, Pg_cplx]
# end of the original part




    
    Pg1 = ((-rd-gr+bl+yw)/(Veg-Vgg+Vee-Vge)+1)/2
    Pg2 = ((-rd-bl+gr+yw)/(Vge-Vgg+Vee-Veg)+1)/2

    V_matrix = np.matrix([[Vgg, Vge, Veg, Vee], [Vge, Vgg, Veg, Vee], 
                          [Veg, Vee, Vgg, Vge], [Vee, Veg, Vge, Vgg]])
    y_vector = [rd, gr, bl, yw]
    P = np.dot(np.linalg.inv(V_matrix), y_vector)


#    Igg = 1
#    Ige = 0.0
#    Ieg = 0.0
#    Iee = 0.0

    Igg = 0.8
    Ige = 0.05
    Ieg = 0.15
    Iee = 0.00
    
    I_matrix = np.matrix([[Igg, Ige, Ieg, Iee], [Ige, Igg, Iee, Ieg], 
                          [Ieg, Iee, Igg, Ige], [Iee, Ieg, Ige, Igg]])
    
    P_correct = np.dot(I_matrix, P)

    Pgg = np.transpose(P_correct[0])
    Pgg= Pgg.A1
    
    fig2, axes2 = plt.subplots(2)
    axes2[0].plot(xs[12:], np.real(Pgg))
    axes2[0].plot(xs[12:], np.real(Pg1*Pg2), color='r')
    axes2[1].plot(xs[12:], np.imag(Pgg))
    
    return [Pgg, Pg1, Pg2]





        
    

class TwoQubit_RB(Measurement1D):
    """Two qubit randomized benchmarking."""

    filepath_lookup_table = ""

    def __init__(self, qubit_info, qubit2_info, twoQ_info, cancel_info, num_cal_points, N_cliffords, generator='CZ', seq=None, postseq=None, num_gates=0, category='all', cnum=None,
                 find_cheapest_recovery=False, interleave=None, use_virtual_Z=False, virtual_recovery=False, use_lookup_table=False,
                 singleQ_phases=[0,0], **kwargs):
        self.qubit_info = qubit_info
        self.qubit2_info = qubit2_info
        self.twoQ_info = twoQ_info
        self.cancel_info = cancel_info
        self.N_cliffords = N_cliffords
        self.num_cal_points = num_cal_points
        XS = np.asarray(range(N_cliffords+4*self.num_cal_points)) - (4*self.num_cal_points-1)
        self.xs = np.array([XS,XS,XS,XS]).transpose().flatten() # for plotting purposes
        self.filepath_lookup_table = ""
        self.cnum=cnum
        self.interleave = interleave
        self.use_virtual_Z = use_virtual_Z
        self.virtual_recovery = virtual_recovery
        self.singleQ_phases = singleQ_phases
        self.use_lookup_table = use_lookup_table
        
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.generator = generator
        self.category = category
        self.find_cheapest_recovery = find_cheapest_recovery
        self.num_gates = num_gates
        
            
        super(TwoQubit_RB, self).__init__(4*(N_cliffords+4*num_cal_points), infos=(qubit_info,qubit2_info,twoQ_info,cancel_info), **kwargs)
        self.data.create_dataset('Cliffords', data=range(4*(N_cliffords+4*num_cal_points)))
#        self.data.set_attrs(
#            cnum=cnum,
#            interleave=interleave
#        )
         

    def generate(self):
        s = Sequence()
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate
        r3 = self.twoQ_info.rotate
        r4 = self.cancel_info.rotate
        q_len1 = self.qubit_info.chop*self.qubit_info.w+self.qubit_info.sq_len
        q_len2 = self.qubit2_info.chop*self.qubit2_info.w+self.qubit2_info.sq_len
        twoQ_len = self.twoQ_info.chop*self.twoQ_info.w+self.twoQ_info.sq_len# + self.cancel_info.chop*self.cancel_info.w+self.cancel_info.sq_len 


#        randomize = config['Randomize']
#        interleave = config['Interleave 2-QB Gate']
#        write_seq = config.get('Write sequence as txt file', False)
        
#        rnd.seed(randomize)

        # Generate 2QB RB sequence
        cliffordSeq1 = []
        cliffordSeq2 = []
        recov_cliffordSeq1 = []
        recov_cliffordSeq2 = []
        pulseSeq1 = []
        pulseSeq2 = []
        recov_pulseSeq1 = []
        recov_pulseSeq2 = []
        len1 = [0]
        len2 = [0]
        recov_len1 = [0]
        recov_len2 = [0]
        phi1 = [0]
        phi2 = [0]
        


        
        self.num_gates = len(cliffordSeq1)

        for j in range(self.num_cal_points):
            s.append(self.seq)
#            temp_seq = Sequence()
#            temp_seq.append(r(np.pi,0))   
            for i in range(4):
                s.append(self.seq)
                s.append(r(np.pi,0))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses qubit 1')


        for j in range(self.num_cal_points):

            temp_seq = Sequence()
            temp_seq.append(r2(np.pi,0))   
            for i in range(4):


                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses qubit 2')


        for j in range(self.num_cal_points):

            temp_seq = Sequence()
            temp_seq.append(Combined([r(np.pi,0),r2(np.pi,0)]))   
            for i in range(4):


                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses for both qubits')

        
        
        for j in range(self.num_cal_points):

            temp_seq = Sequence()
            s.append(Delay(24))   
            for i in range(4):
                s.append(self.seq)
                s.append(Join(temp_seq))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration ground state')


        for m in range(self.N_cliffords):
            clif1 = [['Xp', 'VZ2p', 'X2m', 'VZ2m', 'Ic', 'VZ2p', 'X2p', 'VZ2m', 'Ic', 'VZ2p', 'X2p', 'VZ2m']]
            clif2 =[['X2m', 'VZ2p', 'X2m', 'VZ2m', 'CZ', 'X2m', 'Ip', 'Ip', 'CZ', 'X2p', 'Ip', 'Ip']]
#            clif1 = ['VZ2p', 'Ip', 'Ip', 'Ip', 'Ic', 'VZ2p', 'Xp']
#            clif2=['VZ2p', 'X2p', 'VZp', 'X2m', 'CZ', 'VZ2p', 'Xp']
#            clif1 = ['Xp']
#            clif2=['Xp']


            recov1 =[['VZp', 'X2m', 'VZ2m', 'Ic', 'VZ2p', 'X2p', 'VZ2m', 'Ic', 'VZ2p', 'X2p', 'VZ2m']]
            recov2 = [['X2p', 'Ip', 'Ip', 'CZ', 'X2m', 'Ip', 'Ip', 'CZ', 'X2p', 'Ip', 'Ip']]
            clif1[m].extend(recov1[m])
            clif2[m].extend(recov2[m])
     
            combine_seq=[]
            combine2_seq=[]
            phase1=0
            phase2=0
            r1= self.qubit_info.rotate
            r2= self. qubit2_info.rotate
            r3 = self.twoQ_info.rotate
          
            for ROpostseq in [None, r(np.pi,0), r2(np.pi,0),
                              Combined([r(np.pi,0),r2(np.pi,0)])]:
                s.append(self.seq)
                for i in range(len(clif1[m])):
                    if clif1[m][i] in ['I','Xp', 'X2p', 'Xm', 'X2m', 'Yp', 'Y2p', 'Ym', 'Y2m']:
                        combine_seq.append(self.seq_table1(phase1, clif1[m][i]))
                    if clif2[m][i] in ['I','Xp', 'X2p', 'Xm', 'X2m', 'Yp', 'Y2p', 'Ym', 'Y2m']:
                        combine2_seq.append(self.seq_table2(phase2, clif2[m][i]))
                    if clif1[m][i] in ['Ip', 'VZp', 'VZm', 'VZ2p', 'VZ2m']:
                        phase1 = self.phase_table1(phase1, clif1[m][i])
                    if clif2[m][i] in ['Ip', 'VZp', 'VZm', 'VZ2p', 'VZ2m']:
                        phase2 = self.phase_table2(phase2, clif2[m][i])
                    if clif1[m][i] in ['Ic']:
                        phase1 = phase1 + self.singleQ_phases[0]
                        combine_seq.append(Delay(41))
                    if clif2[m][i] in ['Ic']:
                        phase2 = phase2 + self.singleQ_phases[1]
                        combine2_seq.append(Delay(41))
                    if clif2[m][i] in ['CZ']:
                        phase2 = phase2 + self.singleQ_phases[1]
                        combine2_seq.append(r3(np.pi, ((phase2 % (2*np.pi)))))
                    if clif1[m][i] in ['CZ']:
                        phase1 = phase1 + self.singleQ_phases[0]
                        combine_seq.append(r3(np.pi, ((phase1 % (2*np.pi)))))
                                    
                s.append(Combined([Join(combine_seq), Join(combine2_seq)]))


                if ROpostseq is not None:
                    s.append(ROpostseq)
                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(200))

          
#            # Avoid Error: zero-size array to reduction operation maximum which has no identity (05/05/2019)
#            if (gateSeq1 == [] and gateSeq2 == []):
#                gateSeq1.append(Delay(4*w+sq_len))
#                gateSeq2.append(Delay(4*w+sq_len))
#
#            # test the recovery gate
#            psi_gnd = np.matrix('1; 0; 0; 0') # ground state |00>
#            if write_seq == True:
#                import os
#                from datetime import datetime
#                directory = os.path.join(path_currentdir,'2QB_RBseq')
#                if not os.path.exists(directory):
#                    os.makedirs(directory)
#                filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S-f')[:-3] + '_N_cliffords=%d_seed=%d.txt'%(N_cliffords,randomize)
#                # filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S-%f')[:-3] + '_N_cliffords=%d_seed=%d.txt'%(N_cliffords,randomize)
#                filepath = os.path.join(directory,filename)
#                log.info('make file: ' + filepath)
#                with open(filepath, "w") as text_file:
#                    print('New Sequence', file=text_file)
#                    for i in range(len(gateSeq1)):
#                        print("Index: %d, Gate: ["%(i) + cliffords.Gate_to_strGate(gateSeq1[i]) + ", " + cliffords.Gate_to_strGate(gateSeq2[i]) +']', file=text_file)
#                    for i in range(len(cliffordSeq1)):
#                         print("CliffordIndex: %d, Gate: ["%(i) + cliffords.Gate_to_strGate(cliffordSeq1[i]) + ", " + cliffords.Gate_to_strGate(cliffordSeq2[i]) +']', file=text_file)
#                    for i in range(len(recoverySeq1)):
#                         print("RecoveryIndex: %d, Gate: ["%(i) + cliffords.Gate_to_strGate(recoverySeq1[i]) + ", " + cliffords.Gate_to_strGate(recoverySeq2[i]) +']', file=text_file)
#            psi = np.matmul(evaluate_sequence(gateSeq1, gateSeq2), psi_gnd)
#
#            np.set_printoptions(precision=2)
#            log.info('The matrix of the overall gate sequence:')
#            log.info(evaluate_sequence(gateSeq1, gateSeq2))
#
#            log.info('--- TESTING THE RECOVERY GATE ---')
#            log.info('The probability amplitude of the final state vector: ' + str(np.matrix(psi).flatten()))
#            log.info('The population of the ground state after the gate sequence: %.4f'%(np.abs(psi[0,0])**2))
#            log.info('-------------------------------------------')
#
#
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs




    def seq_table1(self, phase1, symbol):
        r1 = self.qubit_info.rotate
        if symbol == 'I':
            return Delay(24)
        elif symbol == 'Xp':
            return r1(np.pi, ((phase1 % (2*np.pi))))       
        elif symbol == 'X2p':
            return r1(np.pi/2, ((phase1 % (2*np.pi))))
        elif symbol == 'Xm':
            return r1(-np.pi,((phase1 % (2*np.pi))))
        elif symbol == 'X2m':
            return r1(-np.pi/2, ((phase1 % (2*np.pi))))
        elif symbol == 'Yp':
            return r1(np.pi, (phase1 % (2*np.pi))+ np.pi/2)
        elif symbol == 'Y2p':
            return r1(np.pi/2, (phase1 % (2*np.pi))+ np.pi/2)
        elif symbol == 'Ym':
            return r1(-np.pi, (phase1 % (2*np.pi))+ np.pi/2)
        elif symbol == 'Y2m':
            return r1(-np.pi/2, (phase1 % (2*np.pi))+ np.pi/2)       
        
    def phase_table1(self, phase1, symbol):
        if symbol == 'Ip':
            phase1 = phase1
            return phase1
        elif symbol == 'VZp':
            phase1 = (((phase1 % (2*np.pi)))) + np.pi
            return phase1       
        elif symbol == 'VZm':
            phase1 = (((phase1 % (2*np.pi)))) - np.pi
            return phase1       
        elif symbol == 'VZ2p':
            phase1 = (((phase1 % (2*np.pi)))) + np.pi/2
            return phase1       
        elif symbol == 'VZ2m':
            phase1 = (((phase1 % (2*np.pi)))) - np.pi/2
            return phase1       



    def seq_table2(self, phase2, symbol):
        r2 = self.qubit2_info.rotate
        if symbol == 'I':
            return Delay(24)
        elif symbol == 'Xp':
            return r2(np.pi, ((phase2 % (2*np.pi))))       
        elif symbol == 'X2p':
            return r2(np.pi/2, ((phase2 % (2*np.pi))))
        elif symbol == 'Xm':
            return r2(-np.pi,((phase2 % (2*np.pi))))
        elif symbol == 'X2m':
            return r2(-np.pi/2, ((phase2 % (2*np.pi))))
        elif symbol == 'Yp':
            return r2(np.pi, (phase2 % (2*np.pi))+ np.pi/2)
        elif symbol == 'Y2p':
            return r2(np.pi/2, (phase2 % (2*np.pi))+ np.pi/2)
        elif symbol == 'Ym':
            return r2(-np.pi, (phase2 % (2*np.pi))+ np.pi/2)
        elif symbol == 'Y2m':
            return r2(-np.pi/2, (phase2 % (2*np.pi))+ np.pi/2)


    def phase_table2(self, phase2, symbol):
        if symbol == 'Ip':
            phase2 = phase2
            return phase2
        elif symbol == 'VZp':
            phase2 = (((phase2 % (2*np.pi)))) + np.pi
            return phase2       
        elif symbol == 'VZm':
            phase2 = (((phase2 % (2*np.pi)))) - np.pi
            return phase2       
        elif symbol == 'VZ2p':
            phase2 = (((phase2 % (2*np.pi)))) + np.pi/2
            return phase2       
        elif symbol == 'VZ2m':
            phase2 = (((phase2 % (2*np.pi)))) - np.pi/2
            return phase2       



    def analyze(self, data=None, fig=None):
        results = analysis(self, data, fig)
        self.Pgg = results[0]
        self.Pg1 = results[1]
        self.Pg2 = results[2]
        return self.Pgg