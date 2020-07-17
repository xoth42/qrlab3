# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 20:22:15 2020

@author: wanglab
"""

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
    y2d = ys.reshape(len(ys)/2,2)
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    y3s = y2d[:,1] - y2d[:,0]
    fig.axes[0].clear()   
    fig.axes[0].plot(xs, y1s, 'bs', linestyle='-', ms=3)
    fig.axes[0].plot(xs, y2s, 'rs', linestyle='-', ms=3)    
    fig.axes[0].plot(xs, y2s, 'rs', linestyle='--', ms=3)    
    
    for ys in [y1s, y2s, y3s]:
    
        amp0 = -(np.min(ys) - np.max(ys)) / 2
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
#            fig.axes[0].plot(xs, -fit_amprabi(result.params, xs, 0))
            fig.axes[1].plot(xs, fit_amprabi(result.params, xs, ys), marker='s')
    
    
            temporaryy = -fit_amprabi(result.params, xs, 0)
            print(-fit_amprabi(result.params, xs, 0))
            print(xs[np.argmin(temporaryy)], 'min of the fit')
            center_amp_list.append(xs[np.argmin(temporaryy)])
    #        print(min_x, 'This is the value')
            
    #    lmfit.report_fit(params)
            lmfit.report_fit(result.params)
            print ((11*np.pi - result.params['phase'].value ) * result.params['period'].value/(2*np.pi))# Chen 4/3
            
            fig.axes[0].set_ylabel('Intensity [AU]')
            fig.axes[0].set_xlabel('Pulse amplitude')
            fig.axes[0].legend(loc=0)


    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.amps
    y2d = ys.reshape(len(ys)/2,2)
    ys = y2d[:,0] - y2d[:,1]
    fig.axes[0].clear()   
    fig.axes[0].plot(xs, ys, 'bs', ms=3)
#    fig.axes[0].plot(xs, y2s, 'rs', ms=3)    
    

    amp0 = -(np.min(ys) - np.max(ys)) / 2
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
    #       result2 = lmfit.minimize(fit_amprabi_func, result.params, args=(xs, ys, meas))
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
#           fig.axes[0].plot(xs, -fit_amprabi(result.params, xs, 0))
        fig.axes[1].plot(xs, fit_amprabi(result.params, xs, ys), marker='s')
    
    
        temporaryy = -fit_amprabi(result.params, xs, 0)
        print(-fit_amprabi(result.params, xs, 0))
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

class Rabi_singlequbit_compensation(Measurement1D):

    def __init__(self, qubit_info, qubit2_info, amps, update=False, seq=None, seq2 =None, r_axis=0, fix_phase=True, rel_amp=1.0, rel_angle=0.0,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, fit_type=FIT_AMP, **kwargs):
        self.qubit_info = qubit_info
        self.qubit2_info = qubit2_info
        self.amps = amps
#        self.xs = amps
        self.xs = np.array([amps,amps]).transpose().flatten()       # For plotting purposes
        self.update_ins = update
        if seq is None:
            seq = Trigger(250)
        if seq2 is None:
            seq2 = Trigger(250)
        self.seq = seq
        self.seq2=seq2
        self.postseq = postseq
        self.fix_phase = fix_phase
        self.fix_period = fix_period
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis
        self.fit_type = fit_type
        self.selective = selective
        self.rel_angle = rel_angle
        self.rel_amp = rel_amp

        super(Rabi_singlequbit_compensation, self).__init__(len(amps)*2, infos=(qubit_info, qubit2_info), **kwargs)
        self.data.create_dataset('amps', data=amps)


    def generate(self):  #That is the original generate function 
        s = Sequence()
        for i, amp in enumerate(self.amps):
            
            '''Without pi pulse'''
            s.append(self.seq)
            if self.selective==1: #Don't work yet
                s.append(Combined([Repeat(self.qubit_info2.rotate_selective(0, self.r_axis), self.repeat_pulse), Repeat(self.qubit_info.rotate_selective(0, self.r_axis, amp=amp), self.repeat_pulse)]))
            elif self.selective==0.5: #Don't work yet
                s.append(Combined([Repeat(self.qubit_info2.rotate_quasiselective(0, self.r_axis), self.repeat_pulse), Repeat(self.qubit_info.rotate_quasiselective(0, self.r_axis, amp=amp), self.repeat_pulse)]))
            else:
                s.append(self.qubit_info.rotate(0, 0, amp=amp))

            if self.postseq is not None:
                s.append(self.postseq)
            s.append(Delay(20))
            s.append(Combined([
                       Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                       Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                   ]))
            s.append(Delay(3000))

            '''With pi pulse'''
            s.append(self.seq)
            s.append(self.qubit2_info.rotate(np.pi,0))
            if self.selective==1: #Don't work yet
                s.append(Combined([Repeat(self.qubit_info2.rotate_selective(0, self.r_axis), self.repeat_pulse), Repeat(self.qubit_info.rotate_selective(0, self.r_axis, amp=amp), self.repeat_pulse)]))
            elif self.selective==0.5: #Don't work yet
                s.append(Combined([Repeat(self.qubit_info2.rotate_quasiselective(0, self.r_axis), self.repeat_pulse), Repeat(self.qubit_info.rotate_quasiselective(0, self.r_axis, amp=amp), self.repeat_pulse)]))
            else:
                s.append(self.qubit_info.rotate(0, 0, amp=amp))
            s.append(self.qubit2_info.rotate(np.pi,0))
            if self.postseq is not None:
                s.append(self.postseq)
               
            s.append(Delay(20))
            s.append(Combined([
                       Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                       Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                   ]))
            s.append(Delay(3000))


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

        return self.pi_amp

    ''' JEFF. Used to populate data in measuremnt from hdf5 file instead of a measurement for analysis. '''
    def load_data(self, filepath, exp_path):
        return 0
        
        