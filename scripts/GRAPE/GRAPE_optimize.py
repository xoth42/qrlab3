import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement2D
import matplotlib.pyplot as plt
import copy
import mclient
import lmfit

def analysis(meas, data=None, fig=None):
    zs, fig = meas.get_ys_fig(data, fig)
    zs = zs.reshape(len(meas.ys), len(meas.xs))
    xs, ys = meas.get_plotxsys()
    ax = fig.axes[0]
    plt.sca(ax)
    
    
    pc = ax.pcolormesh(xs, ys, zs, cmap=plt.get_cmap('RdBu'))
    fig.colorbar(pc)

    ax.set_xlim(xs.min(), xs.max())
    ax.set_ylim(ys.min(), ys.max())
    ax.set_xlabel('qubit amp')
    ax.set_ylabel('cavity amp')
    fig.canvas.draw()
    
    print('best qubit amp', meas.qubit_amps[np.unravel_index(zs.argmin(), zs.shape)[1]],
          'best cavity amp',  meas.cavity_amps[np.unravel_index(zs.argmin(), zs.shape)[0]])


class GRAPE_optimize(Measurement2D):

    def __init__(self, qubit_info, qubit_probe, cavity_info, qubit_amps, cavity_amps, seq=None, 
                 postseq=None, bgcor=False, zmin=None, zmax=None, **kwargs):
        self.qubit_info = qubit_info
        self.qubit_probe = qubit_probe
        self.cavity_info = cavity_info
        self.qubit_amps = qubit_amps
        self.cavity_amps = cavity_amps
        self.xs = qubit_amps
        self.ys = cavity_amps
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.bgcor= bgcor
        self.t_ge = 354
        self.zmin=zmin
        self.zmax=zmax
        
        npoints = len(qubit_amps) * len(cavity_amps)
        if self.bgcor:
            npoints *= 2
        super(GRAPE_optimize, self).__init__(npoints, infos=[qubit_info, qubit_probe, cavity_info], **kwargs)
        self.data.create_dataset('qubit_amps', data=qubit_amps)
        self.data.create_dataset('cavity_amps', data=cavity_amps)
        self.ampdata = self.data.create_dataset('amplitudes', shape=(len(qubit_amps),len(cavity_amps)))

    def generate(self):
        
        r_p = self.qubit_probe.rotate
        s = Sequence()
        for cav_amp in self.cavity_amps:
            for qt_amp in self.qubit_amps:
                for i_bg in range(2):
                    if i_bg == 1 and not self.bgcor:
                        continue
                    s.append(self.seq)
                    
                    time_shift = 13
                    mod4_qt_I = Join([CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_transmon_1000ns.csv', 
                                                                        qt_amp, chan=self.qubit_info.sideband_channels[0]),
                                                Constant(time_shift, 0, chan=self.qubit_info.sideband_channels[0])])
                    
                    mod4_qt_Q = Join([CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_transmon_q_1000ns.csv', 
                                                                        qt_amp, chan=self.qubit_info.sideband_channels[1]),
                                                Constant(time_shift, 0, chan=self.qubit_info.sideband_channels[1])])
                    
                    mod4_cav_I = Join([Constant(time_shift, 0, chan=self.cavity_info.sideband_channels[0]),
                                                 CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_cavity_1000ns.csv', 
                                                                        cav_amp, chan=self.cavity_info.sideband_channels[0])])
                    
                    mod4_cav_Q = Join([Constant(time_shift, 0, chan=self.cavity_info.sideband_channels[1]),
                                                 CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_cavity_q_1000ns.csv', 
                                                                        cav_amp, chan=self.cavity_info.sideband_channels[1])])
                    mod4_encode = Combined([mod4_qt_I, mod4_qt_Q, mod4_cav_I, mod4_cav_Q])
    
                    s.append(mod4_encode)
                    if i_bg == 0:
#                        s.append(Delay(200))                        
                        s.append(r_p(np.pi/2, X_AXIS))
                        s.append(Delay(self.t_ge))
                        s.append(r_p(-np.pi/2, X_AXIS))
#                        s.append(r_p(np.pi, X_AXIS))  # Chen changed this to a qubit temp measurement
                        
                    if self.postseq is not None:
                        s.append(self.postseq)
                    s.append(Combined([
                            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                        ]))
                    s.append(Delay(2000))
            
        
#        for i in range(10):
#            s.append(self.seq)
#            s.append(Combined([
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ]))
#        
#        for i in range(10):
#            s.append(self.seq)
#            s.append(self.qubit_info.rotate_selective(np.pi, X_AXIS))
#            s.append(Combined([
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ]))
            


        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs
    
    
    
    def get_ys(self, data=None):
        ys = super(GRAPE_optimize, self).get_ys(data)
        if self.bgcor:
#            return (ys[::2]-ys[1::2])*1.0/(1.0-ys[1::2])
            return ys[::2]-ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        

        
        