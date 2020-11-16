import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import matplotlib.pyplot as plt
import copy
import mclient
import lmfit

FIT_AMP         = 'AMP'         # Fit simple sine wave
FIT_AMPFUNC     = 'AMPFUNC'     # Try to fit amplitude curve based on pi/2 and pi amp
FIT_PARABOLA    = 'PARABOLA'    # Fit a parabola (to determine min/max pos)


center_amp_list =[] #Ebru

def fit_amprabi(params, x, data):
    est = params['ofs'].value - params['amp'].value * np.cos(2*np.pi*x / params['period'].value + params['phase'].value)
    return data  - est

def fit_amprabi_func(params, x, data, meas):
    coeffs = np.polyfit([0, params['pi2_amp'].value, params['pi_amp'].value], [0, np.pi/2, np.pi], 2)
    phases = (x**2*coeffs[0] + x*coeffs[1] + coeffs[0]) * meas.repeat_pulse
    est = params['ofs'].value - params['amp'].value * np.cos(phases)
    return data  - est

def analysis(meas, data=None, fig=None):
                    
            
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.amps

    y2d = ys.reshape(len(ys)/4,4)
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    y3s = y2d[:,2]
    y4s = y2d[:,3]

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



    
    plt.figure()  
    plt.plot(rd, 'rs', ms=3, label='rd')
    plt.plot(bl, 'bs', ms=3, label='bl')    
    plt.plot(gr, 'gs', ms=3, label='gr')
    plt.plot(yw, 'ys', ms=3, label='ys')
    plt.legend()    

#qubit1
#    V_matrix = np.matrix([[Vgg, Vge, Veg, Vee], [Vge, Vgg, Veg, Vee], 
#                          [Veg, Vee, Vgg, Vge], [Vee, Veg, Vge, Vgg]])
#
#    y_vector = [rd, gr, bl, yw]
#
#corrected one? qubit 1
#
    V_matrix = np.matrix([[Vgg, Vge, Veg, Vee],  
                          [Vge, Vgg, Vee, Veg], 
                          [Veg, Vee, Vgg, Vge],
                          [Vee, Veg, Vge, Vgg]])

    y_vector = [rd, gr, bl, yw]


###qubit2
#    V_matrix = np.matrix([[Vgg, Veg, Vge, Vee], [Veg, Vgg, Vee, Vge], 
#                          [Vge, Vee, Vgg, Veg], [Vee, Vge, Veg, Vgg]])
#
#
#    y_vector = [rd, bl, gr, yw]
#
    P = np.dot(np.linalg.inv(V_matrix), y_vector)
    Pgg = np.transpose(P[0])
    Pgg= Pgg.A1

    Pge = np.transpose(P[1])
    Pge= Pge.A1

    Peg = np.transpose(P[2])
    Peg= Peg.A1

    Pee = np.transpose(P[3])
    Pee= Pee.A1

    plt.figure()  
    plt.plot(Pgg, 'bs', ms=3, label='Pgg')
    plt.plot(Pge, 'rs', ms=3, label='Pge')    
    plt.plot(Peg, 'gs', ms=3, label='Peg')
    plt.plot(Pee, 'ys', ms=3, label='Pee')
    plt.legend()    





#    fig.axes[0].clear()   
#    fig.axes[0].plot(xs, Pgg, 'bs', ms=3, label='Pgg')
#    fig.axes[0].plot(xs, Pge, 'rs', ms=3, label='Pge')    
#    fig.axes[0].plot(xs, Peg, 'gs', ms=3, label='Peg')
#    fig.axes[0].plot(xs, Pee, 'ys', ms=3, label='Pee')
#    plt.legend()    
#

#
#
    Igg = 0.8
    Ige = 0.05
    Ieg = 0.15
    Iee = 0.00
    
    I_matrix = np.matrix([[Igg, Ige, Ieg, Iee], [Ige, Igg, Iee, Ieg], 
                          [Ieg, Iee, Igg, Ige], [Iee, Ieg, Ige, Igg]])
    

#    Igg = 0.8
#    Ieg = 0.05
#    Ige = 0.15
#    Iee = 0.00
#    
#    I_matrix = np.matrix([[Igg, Ieg, Ige, Iee], [Ieg, Igg, Iee, Ige], 
#                          [Ige, Iee, Igg, Ieg], [Iee, Ige, Ieg, Igg]])
#
#


    P_correct = np.dot(I_matrix, P)

    Pgg = np.transpose(P_correct[0])
    Pgg= Pgg.A1
    Pge = np.transpose(P_correct[1])
    Pge= Pge.A1
    Peg = np.transpose(P_correct[2])
    Peg= Peg.A1
    Pee = np.transpose(P_correct[3])
    Pee= Pee.A1


    plt.figure()  
    plt.plot(Pgg, 'bs', ms=3, label='Pgg')
    plt.plot(Pge, 'rs', ms=3, label='Pge')    
    plt.plot(Peg, 'gs', ms=3, label='Peg')
    plt.plot(Pee, 'ys', ms=3, label='Pee')
    plt.legend()    


    plt.figure()
    plt.plot(Pgg+Peg, label='PgB')
    plt.plot(Pee+Pge, label='PeB')
    plt.plot(Pee+Peg, label='PeA')
    plt.plot(Pgg+Pge, label='PgA')
    plt.legend()       


    for ys in [Pgg, Pge, Peg, Pee]:
#    for ys in [rd, bl, gr, yw]:        
        amp0 = (np.max(ys) - np.min(ys)) / 2
        if ys[len(ys)/2]>np.average(ys):
            amp0 = -amp0
        fftys = np.abs(np.fft.fft(ys - np.average(ys)))
        fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
        period0 = 1 / np.abs(fftfs[np.argmax(fftys)])
    
        params = lmfit.Parameters()
        params.add('ofs', value=np.average(ys))
        params.add('amp', value=amp0)
        params.add('phase', value=0, vary=False)
        #For RB better pi_amp tuning 
    #    params.add('amp', value=amp0) 
    #    params.add('phase', value=-np.pi, min=-np.pi, max=np.pi)
    
        if meas.fit_type == FIT_AMPFUNC:
            pi_amp = period0 * meas.repeat_pulse / 2
            params.add('pi_amp', value=pi_amp)
            params.add('pi2_amp', value=0.5*pi_amp)
            result = lmfit.minimize(fit_amprabi_func, params, args=(xs, ys, meas))
    #        result2 = lmfit.minimize(fit_amprabi_func, result.params, args=(xs, ys, meas))
            txt = ''
            fig.axes[0].plot(xs, -fit_amprabi_func(result.params, xs, 0, meas), label='fit')
            fig.axes[1].plot(xs, fit_amprabi_func(result.params, xs, ys, meas), marker='s')
    
    
    
        else:
            if meas.fix_period is not None:
                params.add('period', value=meas.fix_period, vary=False)
            else:
                params.add('period', value=period0, min=0)
            result = lmfit.minimize(fit_amprabi, params, args=(xs, ys))
            # stderr of 0 is none. replace with other line when using actual data
            #txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.06f' % (result.params['amp'].value, 0, result.params['period'].value, 0, result.params['period'].value/2 )
            txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.06f' % (result.params['amp'].value, 
                                                                                     result.params['amp'].stderr, 
                                                                                     result.params['period'].value, 
                                                                                     result.params['period'].stderr, 
                                                                                     result.params['period'].value/2 )
            fig.axes[0].plot(xs, -fit_amprabi(result.params, xs, 0), label=txt)
            fig.axes[0].plot(xs, -fit_amprabi(result.params, xs, 0))
            fig.axes[1].plot(xs, fit_amprabi(result.params, xs, ys), marker='s')
    
    
            temporaryy = -fit_amprabi(result.params, xs, 0)
    #        print(-fit_amprabi(result.params, xs, 0))
            print(xs[np.argmin(temporaryy)], 'min of the fit')
            center_amp_list.append(xs[np.argmin(temporaryy)])
    #        print(min_x, 'This is the value')
            
    #    lmfit.report_fit(params)
        lmfit.report_fit(result.params)
        print ((11*np.pi - result.params['phase'].value ) * result.params['period'].value/(2*np.pi))# Chen 4/3
        
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Pulse amplitude')
        fig.axes[0].legend(loc=0)

    fig.canvas.draw()



    return result.params

class Rabi(Measurement1D):

    def __init__(self, qubit_info, qubit2_info, amps, update=False, seq=None, r_axis=0, fix_phase=True, cancel_info=None,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, fit_type=FIT_AMP, **kwargs):
        self.qubit_info = qubit_info
        self.qubit2_info  =qubit2_info
        self.cancel_info = cancel_info
        self.amps = amps
        XS = np.asarray(range(len(amps)+4*3)) - (4*3-1)
        self.xs = np.array([XS,XS,XS,XS]).transpose().flatten() / 1e3      # For plotting purposes
        self.update_ins = update
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.fix_phase = fix_phase
        self.fix_period = fix_period
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis
        self.fit_type = fit_type
        self.selective = selective

        
        if cancel_info is not None:
            super(Rabi, self).__init__(4*(len(amps)+12), infos=(qubit_info, qubit2_info, cancel_info), **kwargs)
        else:
            super(Rabi, self).__init__(4*(len(amps)+12), infos=(qubit_info, qubit2_info), **kwargs)
            
        self.data.create_dataset('amps', data=amps)

    def generate(self):  #That is the original generate function 
        s = Sequence()
        r = self.qubit_info.rotate
        r2 = self.qubit2_info.rotate

        for j in range(3):
            s.append(self.seq)
            for i in range(4):
                s.append(self.seq)
                s.append(r(np.pi,0))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses qubit 1')


        for j in range(3):

            s.append(self.seq)
            for i in range(4):


                s.append(self.seq)
                s.append(Join(r2(np.pi,0)))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses qubit 2')


        for j in range(3):

            s.append(self.seq)
  
            for i in range(4):


                s.append(self.seq)
                s.append(Join(Combined([r(np.pi,0),r2(np.pi,0)])))
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration pi pulses for both qubits')

        
        
        for j in range(3):

            s.append(self.seq)

            s.append(Delay(24))   
            for i in range(4):
                s.append(self.seq)
                s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
                s.append(Delay(1000))
        print('appended calibration ground state')



        for i, amp in enumerate(self.amps):
            s.append(self.seq)



            if self.cancel_info is not None:
                for j in range(self.repeat_pulse):
                    s.append(Combined([self.qubit_info.rotate(0, self.r_axis, amp=amp),
                                       self.cancel_info.rotate(np.pi, self.r_axis)
                            ]))
            else:
                if self.selective==1:
                    s.append(Repeat(self.qubit_info.rotate_selective(0, self.r_axis, amp=amp), self.repeat_pulse))
                elif self.selective==0.5:
                    s.append(Repeat(self.qubit_info.rotate_quasilective(0, self.r_axis, amp=amp), self.repeat_pulse))
                else:
                    s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=amp), self.repeat_pulse))
            if self.postseq is not None:
                s.append(self.postseq)
            s.append(Delay(100))
            s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
            s.append(Delay(2000))





            s.append(self.seq)            
            if self.cancel_info is not None:
                for j in range(self.repeat_pulse):
                    s.append(Combined([self.qubit_info.rotate(0, self.r_axis, amp=amp),
                                       self.cancel_info.rotate(np.pi, self.r_axis)
                            ]))
            else:
                if self.selective==1:
                    s.append(Repeat(self.qubit_info.rotate_selective(0, self.r_axis, amp=amp), self.repeat_pulse))
                elif self.selective==0.5:
                    s.append(Repeat(self.qubit_info.rotate_quasilective(0, self.r_axis, amp=amp), self.repeat_pulse))
                else:
                    s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=amp), self.repeat_pulse))
            if self.postseq is not None:
                s.append(self.postseq)
            s.append(Delay(100))
            s.append(r(np.pi,0))
            s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
            s.append(Delay(2000))





            s.append(self.seq)
            if self.cancel_info is not None:
                for j in range(self.repeat_pulse):
                    s.append(Combined([self.qubit_info.rotate(0, self.r_axis, amp=amp),
                                       self.cancel_info.rotate(np.pi, self.r_axis)
                            ]))
            else:
                if self.selective==1:
                    s.append(Repeat(self.qubit_info.rotate_selective(0, self.r_axis, amp=amp), self.repeat_pulse))
                elif self.selective==0.5:
                    s.append(Repeat(self.qubit_info.rotate_quasilective(0, self.r_axis, amp=amp), self.repeat_pulse))
                else:
                    s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=amp), self.repeat_pulse))
            if self.postseq is not None:
                s.append(self.postseq)
            s.append(Delay(100))
            s.append(r2(np.pi,0))
            s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
            s.append(Delay(2000))




            s.append(self.seq)
            if self.cancel_info is not None:
                for j in range(self.repeat_pulse):
                    s.append(Combined([self.qubit_info.rotate(0, self.r_axis, amp=amp),
                                       self.cancel_info.rotate(np.pi, self.r_axis)
                            ]))
            else:
                if self.selective==1:
                    s.append(Repeat(self.qubit_info.rotate_selective(0, self.r_axis, amp=amp), self.repeat_pulse))
                elif self.selective==0.5:
                    s.append(Repeat(self.qubit_info.rotate_quasilective(0, self.r_axis, amp=amp), self.repeat_pulse))
                else:
                    s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=amp), self.repeat_pulse))

            if self.postseq is not None:
                s.append(self.postseq)            
            s.append(Delay(100))
            s.append(Combined([r(np.pi,0),r2(np.pi,0)]))
            s.append(Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
            s.append(Delay(2000))














        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

#    def generate(self): #Ebru: I am playing with this one
#        s = Sequence()
#        s.append(Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan))  #acquisition
#        for i, amp in enumerate(self.amps):
#            s.append(self.seq)           
#            if self.selective==1:
#                s.append(Repeat(self.qubit_info.rotate_selective(0, self.r_axis, amp=amp), self.repeat_pulse))
#            elif self.selective==0.5:
#                s.append(Repeat(self.qubit_info.rotate_quasilective(0, self.r_axis, amp=amp), self.repeat_pulse))
#            else:
#                s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=amp), self.repeat_pulse))
#            if self.postseq is not None:
#                s.append(self.postseq)
#            s.append(Delay(200))
#            s.append(Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan))
#            s.append(Delay(2000))
#
#
#
#        s = self.get_sequencer(s)
#        seqs = s.render()
#        return seqs
    
    
    def analyze(self, data=None, fig=None):
        if self.fit_type == FIT_PARABOLA:
            if self.repeat_pulse%2 == 0:
                self.pi_amp = 0
                self.pi2_amp = self.analyze_parabola(data=data, fig=fig, xlabel='Amplitude', ylabel='Signal')
            else:
                self.pi_amp = self.analyze_parabola(data=data, fig=fig, xlabel='Amplitude', ylabel='Signal')
                self.pi2_amp = 0

        elif self.fit_type == FIT_AMPFUNC:
            self.fit_params = analysis(self, data=data, fig=fig)
            self.pi_amp = self.fit_params['pi_amp'].value
            self.pi2_amp = self.fit_params['pi2_amp'].value
        else:
            self.fit_params = analysis(self, data=data, fig=fig)
            self.pi_amp = self.fit_params['period'].value / 2 * self.repeat_pulse
            self.pi2_amp = 0

        if self.update_ins:
            print 'Setting qubit pi-rotation ampltidue to %.06f, pi/2 to %.06f' % (self.pi_amp, self.pi2_amp)
            if self.selective==1:
                if self.pi_amp:
                    mclient.instruments[self.qubit_info.insname].set_pi_amp_selective(self.pi_amp)
                if self.pi2_amp:
                    mclient.instruments[self.qubit_info.insname].set_pi2_amp_selective(self.pi2_amp)
            elif self.selective==0.5:
                if self.pi_amp:
                    mclient.instruments[self.qubit_info.insname].set_pi_amp_quasilective(self.pi_amp)
                if self.pi2_amp:
                    mclient.instruments[self.qubit_info.insname].set_pi2_amp_quasilective(self.pi2_amp)
            else:
                if self.pi_amp:
                    mclient.instruments[self.qubit_info.insname].set_pi_amp(self.pi_amp)
                if self.pi2_amp:
                    mclient.instruments[self.qubit_info.insname].set_pi2_amp(self.pi2_amp)


        return self.pi_amp,

    ''' JEFF. Used to populate data in measuremnt from hdf5 file instead of a measurement for analysis. '''
    def load_data(self, filepath, exp_path):
        return 0
        
 
