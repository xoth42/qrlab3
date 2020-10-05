import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
#import lmfit


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = np.linspace(0,5,6)

    y2d = ys.reshape(len(ys)/6,6)
    y1s = y2d[0,:]
    y2s = y2d[1,:]
    y3s = y2d[2,:]
    y4s = y2d[3,:]
    
    fig.axes[0].clear()   
    fig.axes[0].plot(xs, y1s, label='pre X(P/2)')
    fig.axes[0].plot(xs, y2s, label = 'pre X(-P/2)')    
    fig.axes[0].plot(xs, y3s, label='pre Y(P/2)')
    fig.axes[0].plot(xs, y4s, label='pre Y(-P/2)')    
    
    fig.canvas.draw()
    fig.axes[0].legend(loc=0)

    return


class Single_qubit_tomo(Measurement1D):

    def __init__(self, qubit_info, ZZ_info, CZ = False, repeat_pulse=1, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.ZZ_info=ZZ_info
        self.CZ = CZ
        self.repeat_pulse = repeat_pulse
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        super(Single_qubit_tomo, self).__init__(24, infos=(qubit_info,ZZ_info), **kwargs)
        self.data.create_dataset('direction', data=np.linspace(0,23,24))
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate
        for seq2 in [r(np.pi/2,0), r(-np.pi/2,0), r(np.pi/2, np.pi/2), r(-np.pi/2, np.pi/2)]:                          
            '''measure sigma x'''
            s.append(self.seq)
            s.append(seq2)
            if self.CZ == True:        
                s.append(Repeat(self.ZZ_info.rotate(np.pi,0), self.repeat_pulse))
    
            s.append(r(-np.pi/2, Y_AXIS))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            '''measure sigma x'''
            s.append(self.seq)
            s.append(seq2)
            if self.CZ == True:        
                s.append(Repeat(self.ZZ_info.rotate(np.pi,0), self.repeat_pulse))
            s.append(r(-np.pi/2, Y_AXIS))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                
            '''measure sigma y'''
            s.append(self.seq)
            s.append(seq2)
            if self.CZ == True:        
                s.append(Repeat(self.ZZ_info.rotate(np.pi,0), self.repeat_pulse))
    
            s.append(r(np.pi/2, X_AXIS))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            '''measure sigma y'''
            s.append(self.seq)
            s.append(seq2)
            if self.CZ == True:        
                s.append(Repeat(self.ZZ_info.rotate(np.pi,0), self.repeat_pulse))
    
            s.append(r(np.pi/2, X_AXIS))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
           
            '''measure sigma z'''
            s.append(self.seq)
            s.append(seq2)
            if self.CZ == True:        
                s.append(Repeat(self.ZZ_info.rotate(np.pi,0), self.repeat_pulse))
    
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            '''measure sigma z'''
            s.append(self.seq)
            s.append(seq2)
            if self.CZ == True:        
                s.append(Repeat(self.ZZ_info.rotate(np.pi,0), self.repeat_pulse))
    
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))

        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
        return #self.fit_params['tau'].value
