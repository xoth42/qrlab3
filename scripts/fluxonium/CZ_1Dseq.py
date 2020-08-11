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

def fit_timerabi(params, x, data):
    est = (params['ofs'].value - np.exp(-x / params['tau']) *params['amp'].value 
            * np.cos(2*np.pi*x / params['period'].value + params['phase'].value))
    return data  - est



def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.times

    y2d = ys.reshape(len(ys)/2,2)
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    fig.axes[0].clear()   
    fig.axes[0].plot(xs, y1s, 'bs', ms=3)
    fig.axes[0].plot(xs, y2s, 'rs', ms=3)    

    for ys in [y1s, y2s]:
        
        amp0 = -(np.min(ys) - np.max(ys)) / 2
    #    if ys[0]>np.average(ys):
    #        amp0 = -amp0
        fftys = np.abs(np.fft.fft(ys - np.average(ys)))
        fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
        period0 = 1 / np.abs(fftfs[np.argmax(fftys)])
    
        params = lmfit.Parameters()
        params.add('ofs', value=np.average(ys))
        params.add('amp', value=amp0)
        params.add('phase', value=0, min=-np.pi, max=np.pi)
        params.add('tau', value=np.max(xs))
        params.add('period', value=period0, min=0)
        
        result = lmfit.minimize(fit_timerabi, params, args=(xs, ys))
        # stderr of 0 is none. replace with other line when using actual data
        #txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.06f' % (result.params['amp'].value, 0, result.params['period'].value, 0, result.params['period'].value/2 )
        txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi time = %.06f' % (result.params['amp'].value, 
                                                                                 result.params['amp'].stderr, 
                                                                                 result.params['period'].value, 
                                                                                 result.params['period'].stderr, 
                                                                                 result.params['period'].value/2 )
        fig.axes[0].plot(xs, -fit_timerabi(result.params, xs, 0), label=txt)
        fig.axes[1].plot(xs, fit_timerabi(result.params, xs, ys), marker='s')
    
        lmfit.report_fit(result.params)
    
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Pulse time')
        fig.axes[0].legend(loc=0)
    
    fig.canvas.draw()
    return
#    return result.params

class TimeRabi_interleaved(Measurement1D):

    def __init__(self, gate_info1, gate_info2, offset_info, times,sigma=5, update=False, seq=None, r_axis=0, fix_phase=True, read_on_e=True,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, swap_chs = False, fit_type=FIT_AMP, **kwargs):
        self.gate_info1 = gate_info1
        self.gate_info2 = gate_info2
        self.offset_info = offset_info
        self.times = times
        self.xs = np.array([times,times]).transpose().flatten() / 1e3      # For plotting purposes
        self.update_ins = update
        if seq is None:
            seq = Trigger(1000)
        self.seq = seq
        self.postseq = postseq
        self.fix_phase = fix_phase
        self.fix_period = fix_period
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis
        self.fit_type = fit_type
        self.selective = selective
        self.swap_chs = swap_chs
        self.sigma = sigma
        self.read_on_e = read_on_e
        super(TimeRabi_interleaved, self).__init__(len(times)*2, infos=(gate_info1,gate_info2,offset_info), **kwargs)
        self.data.create_dataset('times', data=times)

    def generate(self):
        s = Sequence()
        chs2 = self.offset_info.sideband_channels

            
        for plen in self.times:
            
            '''Without pi pulse'''
            s.append(self.seq)    

            if plen >= 0:
                s.append(self.gate_info1.rotate(np.pi/2,0))
#                s.append(Combined([Constant(int(plen),  0.008, chan=chs2[0]),
#                                   Constant(int(plen), -0.0713, chan=chs2[1])]))
                s.append(Delay(int(plen)))
                s.append(Combined([self.gate_info2.rotate(np.pi,0), self.gate_info1.rotate(np.pi,0)]))
#                s.append(Combined([Constant(int(plen),  0.008, chan=chs2[0]),
#                                   Constant(int(plen), -0.0713, chan=chs2[1])]))
                s.append(Delay(int(plen)))
                s.append(self.gate_info1.rotate(np.pi/2,0))
    
            s.append(Delay(5))
            
            if self.read_on_e is True:
                s.append(self.gate_info2.rotate(np.pi,0))#Chen changed to always measure with control qubit in e
#this part out for the moment

            if self.postseq:
                s.append(self.postseq)
            s.append(Delay(10))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
            s.append(Delay(3000))
            
            '''same as without pi pulse'''

            s.append(self.seq)
            if plen >= 0:
                s.append(self.gate_info1.rotate(np.pi/2,0))
                s.append(Delay(int(plen)))

#                s.append(Combined([Constant(int(plen),  0.008, chan=chs2[0]),
#                                   Constant(int(plen), -0.0713, chan=chs2[1])]))
                s.append(Combined([self.gate_info2.rotate(np.pi,0), self.gate_info1.rotate(np.pi,0)]))
                s.append(Delay(int(plen)))

#                s.append(Combined([Constant(int(plen),  0.008, chan=chs2[0]),
#                                   Constant(int(plen), -0.0713, chan=chs2[1])]))
                s.append(self.gate_info1.rotate(np.pi/2,0))
    
            s.append(Delay(5))
            
            if self.read_on_e is True:
                s.append(self.gate_info2.rotate(np.pi,0))#Chen changed to always measure with control qubit in e
            
            if self.postseq:
                s.append(self.postseq)
            s.append(Delay(10))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
            s.append(Delay(3000))
            
            
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs


    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig)
