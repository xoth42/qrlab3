from measurement import Measurement1D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import objectsharer as objsh
import time
import numpy as np

SPEC   = 0
AMP  = 1

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    fig.axes[0].clear()
    amps = meas.amps
    freqs = meas.freqs
    
    data = np.reshape(ys, (len(amps), len(freqs)))
    
    try: # This is a placeholder until stes is implemented w/ Alazar.
        eb = np.reshape(meas.get_errorbars(), (len(amps), len(freqs)))
    except:
        eb = np.zeros_like(data)
        print('passed no errorbars')  
    
    if meas.plot_type == SPEC:
        for iamp, amp in enumerate(amps):
            fig.axes[0].plot(freqs/1e6, data[iamp,:], label='ro info amp %.03f '%amp)
            fig.axes[0].errorbar(freqs/1e6, data[iamp,:], yerr=eb[iamp,:], fmt='.', 
                         markersize = 0, ecolor='grey', linewidth=1)
        fs = freqs
        amps = data[0,:]
        f = fit.Lorentzian(fs, amps)
        h0 = np.max(amps)
        w0 = 2e6
        pos = fs[np.argmax(amps)]
        p0 = [np.min(amps), w0*h0, pos, w0]
        p = f.fit(p0)
        txt = 'Center = %.03f MHz' % (p[2]/1e6,)
        print 'Fit gave: %s' % (txt,)
#        plt.plot(fs/1e6, f.func(p, fs), label=txt)

        fig.axes[0].legend()
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('Frequency [MHz]')
        

    if meas.plot_type == AMP:
#        ax1 = f.add_subplot(2,1,1)
#        ax2 = f.add_subplot(2,1,2)
        for ifreq, freq in enumerate(freqs):
            fig.axes[0].plot(amps, data[:,ifreq], label='RF @ %.03f MHz'%(freq/1e6,))
            fig.axes[0].errorbar(amps, data[:,ifreq], yerr=eb[:,ifreq], fmt='.', 
                         markersize = 0, ecolor='grey', linewidth=1)
        fig.axes[0].legend()
        fig.axes[0].set_ylabel('Intensity [AU]')
        fig.axes[0].set_xlabel('ro info amp [AU]')

class ROCavSpec_IQ(Measurement1D):

    def __init__(self, qubit_info, amps, freqs, plot_type=None, qubit_pulse=False, seq=None,  
                 comb_list = [], **kwargs):
        self.qubit_info = qubit_info
        self.freqs = freqs
        self.amps = amps
        self.qubit_pulse = qubit_pulse
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.comb_list = comb_list


        if plot_type is None:
            if len(amps) > len(freqs):
                plot_type = AMP
            else:
                plot_type = SPEC
        self.plot_type = plot_type

        super(ROCavSpec_IQ, self).__init__(len(amps)*len(freqs), infos=(qubit_info,), 
                                          **kwargs)
        self.data.create_dataset('amps', data=amps)
        self.data.create_dataset('freqs', data=freqs)

    def generate(self):
        s = Sequence()
        for amp in self.amps:
            for df in self.freqs:
                s.append(self.seq)
                if self.qubit_pulse:
                    s.append(self.qubit_info.rotate(np.pi, 0))
                
                ro_seq = self.readout_driver.do_get_sequence(self.readout_qubit_info,
                                                             df = df, amp = amp)
                poly_seq = [ro_seq]
                for comb in self.comb_list:
                    poly_seq += comb.get_poly_seq(ro_seq.get_length() - comb.sigma*4, df)
                    
                s.append(Combined(poly_seq))

                s.append(Delay(2000))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs



    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)
