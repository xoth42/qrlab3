# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 13:03:57 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 13:57:53 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 15:28:42 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 17:51:18 2020

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import lmfit

ECHO_NONE       = 'NONE'
ECHO_HAHN       = 'HANN'
ECHO_CPMG       = 'CMPG'
ECHO_XY4        = 'XY4'
ECHO_XY8        = 'XY8'
ECHO_XY16       = 'XY16'

def t2_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-c * x) * sin(d * x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    exp = np.exp(-(x / params['tau'].value))
    est = params['ofs'].value + params['amp'].value * exp * sine
    return data - est

def double_sin_fit(params, x, data):
    '''
    Double exponentially decaying sine
    fit function: of + a1 * exp(-tau1 * x) * sin(f1 * x + phi1) + a2 * exp(-tau2 * x) * cos(f2 * x + phi2)
    '''
    exp1 = np.exp(-(x / params['tau'].value))
    exp2 = np.exp(-(x / params['tau'].value))#exp2 = np.exp(-(x / params['tau2'].value))  #Chen changed to single tau for both frequencies 8/24/19
    sin1 = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    sin2 = np.sin(2 * np.pi * x * params['freq2'].value + params['phi2'].value)
    est = params['ofs'].value + params['amp'].value * exp1 * sin1 + params['amp2'].value * exp2 * sin2
    return data - est

def changing_freq_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-(c + f*exp(-s*x)) * x) * sin((d + g*exp(-s*x))* x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * (params['freq'].value + params['A']*np.exp(-params['slope'].value * x) ) + params['phi0'].value)
    exp = np.exp(-(x*(1 / params['tau'].value + params['A2'].value*np.exp(-x*params['slope'].value/2))))
    est = params['ofs'].value + params['amp'].value * exp * sine
    return data - est

def analysis(meas, data=None, fig=None):
    xs = meas.delays
    seq_num = 2
    ys_tot, fig = meas.get_ys_fig(data, fig)
    fig.axes[0].clear()
   
    ys_als = np.zeros([seq_num + 1, len(xs)])
    ys_als[0] = ys_tot[0::seq_num]
    ys_als[1] = ys_tot[1::seq_num]
    ys_cplx = meas.avg_data

#    ys_als[2] = np.angle((ys_cplx[0::seq_num] + ys_cplx[1::seq_num])/2)*180/np.pi #phase
#    ys_als[2] = np.abs((ys_cplx[0::seq_num] + ys_cplx[1::seq_num])/2) #amplitude
    if meas.proj_func == 'phase':
        ys_als[2] = np.angle((ys_cplx[0::seq_num] + ys_cplx[1::seq_num])/2)*180/np.pi
    elif meas.proj_func == 'amplitude':
        ys_als[2] = np.abs((ys_cplx[0::seq_num] + ys_cplx[1::seq_num])/2)
    elif meas.proj_func == 'projection':
        IQg = meas.readout_info.IQg
        IQe = meas.readout_info.IQe

        ys = ((ys_cplx[0::seq_num] + ys_cplx[1::seq_num])/2)- IQg
        if IQg is None or IQe is None or IQg == 0 or IQe == 0:
            p = np.polyfit(np.real(ys), np.imag(ys), 1)
            vproj = 1 + 1j*p[0]
#            return np.real(ys * np.exp(-1j * np.angle(np.average(ys))))
        else:
            vproj = IQe - IQg
        vproj /= np.abs(vproj)
        ys_als[2] = np.real(ys) * vproj.real  + np.imag(ys) * vproj.imag

    if np.max(ys_als) - np.min(ys_als)>300:# and meas.proj_func is 'phase':
        for i in range(len(ys_als)):
            for iphase in range(len(ys_als[0])):
                if ys_als[i][iphase] > 0:
                    ys_als[i][iphase] = ys_als[i][iphase] -360 
    
    fig.axes[0].plot(xs/1e3, ys_als[0], 'bs', ms=3)
    fig.axes[0].plot(xs/1e3, ys_als[1], 'ys', ms=3)
    fig.axes[0].plot(xs/1e3, ys_als[2], 'gs', ms=3)
#    fig.axes[0].plot(xs/1e3, ys_tot[2::seq_num], 'gs', ms=3)
#    fig.axes[0].plot(xs/1e3, ys_tot[3::seq_num], 'rs', ms=3)
#    labels = ['without qubit','without qubit, delay %s'%(meas.delay), 'with qubit','with qubit, delay %s'%(meas.delay)]
#    labels = ['without qubit, delay %s'%(meas.delay),'with qubit, delay %s'%(meas.delay)]
#    labels = ['without qubit, delay %s'%(meas.delay),'without qubit', 'with qubit','with qubit, delay %s'%(meas.delay)]
    labels = ['phase 0','phase pi','averaged phase']
    return_result = []
    for i in range(seq_num+1):
        ys = ys_als[i]
        
        amp0 = (np.max(ys) - np.min(ys)) / 2
        fftys = np.abs(np.fft.fft(ys - np.average(ys)))
        fftfs = np.fft.fftfreq(len(ys), np.abs(xs[1]-xs[0]))
        f0 = np.abs(fftfs[np.argmax(fftys)])
        print('Delta f estimate: %.03f kHz' % (f0 * 1e6))
    
        params = lmfit.Parameters()
        params.add('ofs', value=np.average(ys))
        params.add('amp', value=amp0, min=0.1)
        params.add('tau', value=max(xs), min=1, max=2e7)
        params.add('freq', value=f0, min=0)
        params.add('slope', value=0,vary = False)
        params.add('A', value = 0, vary = False)
        params.add('A2', value = 0, vary = False)
    #    if meas.echotype == ECHO_NONE:
    #
    #        params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)  #Changed to plus sign for accommodate for amplitude RO, need a good LT solution
    #
    #    elif meas.echotype == ECHO_HAHN:
    #        params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi) #DARIO added to fit better for echo vs plain T2
        if  meas.fix_phi0 is None:
            if ys[0] < np.average(ys):
                params.add('phi0', value=-np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True)
            else:
                params.add('phi0', value=np.pi/2, min=-1.2*np.pi, max=1.2*np.pi, vary=True) #Yingying changed phi0 to checking value of first point
        else:
            params.add('phi0', value=meas.fix_phi0, vary=False)
#        else:
#            params.add('phi0',value = return_result[0]['phi0'].value, vary = False)
        result = lmfit.minimize(changing_freq_fit, params, args=(xs, ys))
    #    lmfit.report_fit(params)
    #    result2 = lmfit.minimize(t2_fit, result.params, args=(xs,ys))
        lmfit.report_fit(result.params)
        
        if meas.double_freq == False:
            return_result.append(result.params)
            fig.axes[0].plot(xs/1e3, -changing_freq_fit(result.params, xs, 0), 
                    label='Fit, tau=%.03f us, df=%.03f kHz, %s'%(
                            result.params['tau'].value/1000,
                            result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[0]*result.params['slope']),
#                            result.params['freq'].value*1e6 + result.params['A']*1e6*np.exp(-xs[-1]*result.params['slope'])))
                            labels[i]))
            fig.axes[0].legend()
            fig.axes[0].set_ylabel('Intensity [AU]')
            fig.axes[0].set_xlabel('Time [us]')
            fig.axes[1].plot(xs/1e3, changing_freq_fit(result.params, xs, ys), marker='s')
            fig.canvas.draw()
    
        if meas.double_freq == True:
    
            residues = t2_fit(result.params, xs, ys)
            amp0 = (np.max(residues) - np.min(residues)) / 2
            fftys = np.abs(np.fft.fft(residues - np.average(residues)))
            fftfs = np.fft.fftfreq(len(residues), xs[1]-xs[0])
            f0 = np.abs(fftfs[np.argmax(fftys)])
            print('Delta f estimate: %.03f kHz' % (f0 * 1e6))
    
            params2 = lmfit.Parameters()
            params2.add('ofs', value=amp0)
            params2.add('amp', value=amp0, min=0)
            params2.add('tau', value=xs[-1], min=10, max=200000)
            params2.add('freq', value=meas.detune/1e9, min=0)
            params2.add('phi0', value=-np.pi/2.0, min=-1.2*np.pi, max=1.2*np.pi)
            result = lmfit.minimize(t2_fit, params2, args=(xs, residues))
            lmfit.report_fit(result.params)
    #        fig.axes[1].plot(xs/1e3, -t2_fit(result.params, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz'%(result.params['tau'].value/1000, result.params['freq'].value*1e6))
            fig.axes[1].legend()
    
            params3 = lmfit.Parameters()
            params3.add('ofs', value=params['ofs'].value)
            params3.add('amp', value=params['amp'].value, min=0, max=params['amp'].value*2)
            params3.add('tau', value=params['tau'].value, min=10, max=200000)
            params3.add('freq', value=params['freq'].value, min=0, max=20e-3)
            params3.add('phi0', value=params['phi0'].value, min=-1.2*np.pi, max=1.2*np.pi)
            params3.add('amp2', value=result.params['amp'].value, min=0, max=params['amp'].value*2)
    #        params3.add('tau2', value=result.params['tau'].value, min=10, max=200000)
            params3.add('freq2', value=result.params['freq'].value, min=0, max=20e-3)
            params3.add('phi2', value=result.params['phi0'].value, min=-1.2*np.pi, max=1.2*np.pi)
    
            result = lmfit.minimize(double_sin_fit, params3, args=(xs,ys))
            lmfit.report_fit(result.params)
            text = 'Fit, tau1=%.03f us, df1=%.03f kHz, amp1=%.02f \nFit, tau2=%.03f us, df2=%.03f kHz, amp2=%.02f, %s'%(
                    result.params['tau'].value/1000, result.params['freq'].value*1e6, result.params['amp'].value, 
                    result.params['tau'].value/1000, result.params['freq2'].value*1e6, result.params['amp2'].value,
                    labels[i])
            fig.axes[0].plot(xs/1e3, -double_sin_fit(result.params, xs, 0), label=text)
            fig.axes[0].legend()
            fig.axes[0].set_ylabel('Intensity [AU]')
            fig.axes[0].set_xlabel('Time [us]')
            fig.axes[1].plot(xs/1e3, double_sin_fit(result.params, xs, ys), marker='s')
            fig.canvas.draw()
            return_result.append(result.params)
#            return params3

    return return_result

class CW_Ramsey_Mixer(Measurement1D):

    def __init__(self, qubit_info, SS_mixer_info1, mixer_info1,mixer_info2, delays, detune=0, fix_phi0 = None, delay = 0, qubit_pulse=False,
                 double_freq=False, seq=None, postseq=None, selective=False, Qswitch_infoA=None, Qswitch_infoB=None, **kwargs):
        self.qubit_info = qubit_info
        self.SS_mixer_info1 = SS_mixer_info1
        self.mixer_info1 = mixer_info1
        self.mixer_info2 = mixer_info2
        self.qubit_pulse = qubit_pulse
#        self.timescale = timescale
#        self.qubit_pre = qubit_pre
        self.delays = delays
#        self.xs = delays / 1e3        # For plotting purposes
        self.xs = np.array([delays,delays]).transpose().flatten() / 1e3      # For plotting purposes
        self.detune = detune
        self.delay = delay
        self.fix_phi0 = fix_phi0
        self.double_freq=double_freq
        if seq is None:
            seq = Trigger(250)
#            seq = [Trigger(250)]
        self.seq = seq
        self.postseq = postseq
        self.selective = selective     # Added 9/29 for Ramsey measuring chi
        self.QswA = Qswitch_infoA
        self.QswB = Qswitch_infoB

        super(CW_Ramsey_Mixer, self).__init__(len(delays)*2, infos=(qubit_info,SS_mixer_info1, mixer_info1,mixer_info2,), **kwargs)
        self.data.create_dataset('delays', data=delays)
        self.data.set_attrs(
            detune=detune,
        )



    def generate(self):
        ro_delay = 500
        s = Sequence()
        s.append(self.seq)
        s.append(Delay(2000))
        ro = (Combined([
            Join([Delay(200),Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]),
#            Join([Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),Delay(200)]),
            Join([self.mixer_info1.rotate(np.pi, 0),Delay(200)]),
            Join([self.mixer_info2.rotate(np.pi, 0),Delay(200)])
#                Join([Delay(100),Constant(self.readout_info.pulse_len, self.mixer_info.pi_amp, chan=self.mixer_info.channels[0]),Delay(200)]),
        ]))
#    we are using the rotate_selective for the single photon stuff and the rotate for stark shift stuff
        if self.selective == True:
            pi_amp = self.SS_mixer_info1.pi_amp_selective
            print('Selective')
        else:
            pi_amp = self.SS_mixer_info1.pi_amp
        
        r = self.qubit_info.rotate

        for i, dt in enumerate(self.delays):
#            """
            
            ''' ramsey with phase 0'''
            s.append(self.seq)
#            s.append(Delay(300))
            angle = dt * 1e-9 * self.detune * 2 * np.pi
            if dt > 0:
                s.append(Combined([
                        Join([Constant(int(10000 + 4*self.qubit_info.w + dt + 4*self.qubit_info.w), pi_amp, chan = self.SS_mixer_info1.sideband_channels[0])]),
                        Join([Delay(10000),
                              r(np.pi/2, X_AXIS),
                              Delay(int(dt)),
                              r(-np.pi/2, angle),                          
                                ])
                        ]))
            else:
                s.append(Combined([
                        Join([Constant(int(10000 + 4*self.qubit_info.w + dt + 4*self.qubit_info.w), pi_amp, chan = self.SS_mixer_info1.sideband_channels[0])]),
                        Join([Delay(10000),
                              r(np.pi/2, X_AXIS),
#                              Delay(int(dt)),
                              r(-np.pi/2, angle),                          
                                ])
                        ]))
            if self.postseq:
                s.append(self.postseq)
                
            s.append(Delay(ro_delay))
            s.append(ro)
            s.append(Delay(2000))
            
            
            ''' ramsey with phase pi '''
            s.append(self.seq)
#            s.append(Delay(300))
            angle = dt * 1e-9 * self.detune * 2 * np.pi
            if dt >0:                     
                s.append(Combined([
                        Join([Constant(int(10000 + 4*self.qubit_info.w + dt + 4*self.qubit_info.w), -pi_amp, chan = self.SS_mixer_info1.sideband_channels[0])]),
                        Join([Delay(10000),
                              r(np.pi/2, X_AXIS),
                              Delay(int(dt)),
                              r(-np.pi/2, angle),                          
                                ])
                        ]))
            else:
                s.append(Combined([
                        Join([Constant(int(10000 + 4*self.qubit_info.w + dt + 4*self.qubit_info.w), -pi_amp, chan = self.SS_mixer_info1.sideband_channels[0])]),
                        Join([Delay(10000),
                              r(np.pi/2, X_AXIS),
#                              Delay(int(dt)),
                              r(-np.pi/2, angle),                          
                                ])
                        ]))                
            if self.postseq:
                s.append(self.postseq)
            s.append(Delay(ro_delay))
            s.append(ro)
            s.append(Delay(2000))



        s = self.get_sequencer(s)
        seqs = s.render()
#        s.plot_seqs(seqs)

        return seqs
    
    
      

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
#        return self.fit_params['tau'].value
