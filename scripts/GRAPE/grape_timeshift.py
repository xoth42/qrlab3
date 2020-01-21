import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.xs
    fig.axes[0].plot(xs, ys, '.')
    fig.axes[0].set_xlabel('relative delay')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()

class grape_timeshift(Measurement1D):

    def __init__(self, qubit_info, qubit_probe, cavity_info, rel_delays, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.qubit_probe = qubit_probe
        self.cavity_info = cavity_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.rel_delays = rel_delays
        self.xs = rel_delays
        self.t_ge = 354

        npoints = len(rel_delays)
        super(grape_timeshift, self).__init__(npoints, residuals=False, infos=[qubit_info, qubit_probe, cavity_info], **kwargs)
        self.data.create_dataset('rel_delays', data=rel_delays)

    def generate(self):
        s = Sequence()
        r_p = self.qubit_probe.rotate
        cav_amp = 102
        qt_amp = 44
        
        grape_t = CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_transmon_1000ns.csv', qt_amp, chan=self.qubit_info.sideband_channels[0])
        grape_c = CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_cavity_1000ns.csv', cav_amp, chan=self.cavity_info.sideband_channels[0])
                           
        for dt in self.rel_delays:
            s.append(self.seq)
            if dt < 0:
                s.append(Combined([Join([Constant(int(-dt), 0, chan=self.qubit_info.sideband_channels[0]), grape_t]),
                                   Join([grape_c, 
                                         Constant(int(-dt), 0, chan=self.cavity_info.sideband_channels[0])])
                        ]))
            elif dt > 0:
                mod4_qt_I = Join([CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_transmon_1000ns.csv', 
                                                                    qt_amp, chan=self.qubit_info.sideband_channels[0]),
                                            Constant(dt, 0, chan=self.qubit_info.sideband_channels[0])])
                
                mod4_qt_Q = Join([CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_transmon_q_1000ns.csv', 
                                                                    qt_amp, chan=self.qubit_info.sideband_channels[1]),
                                            Constant(dt, 0, chan=self.qubit_info.sideband_channels[1])])
                
                mod4_cav_I = Join([Constant(dt, 0, chan=self.cavity_info.sideband_channels[0]),
                                             CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_cavity_1000ns.csv', 
                                                                    cav_amp, chan=self.cavity_info.sideband_channels[0])])
                
                mod4_cav_Q = Join([Constant(dt, 0, chan=self.cavity_info.sideband_channels[1]),
                                             CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\encoding_unitary_cavity_q_1000ns.csv', 
                                                                    cav_amp, chan=self.cavity_info.sideband_channels[1])])
                
                mod4_encode = Combined([mod4_qt_I, mod4_qt_Q, mod4_cav_I, mod4_cav_Q])

                s.append(mod4_encode)  #Chen temporary 10/12
#                s.append(Combined([Join([grape_t,
#                                         Constant(int(dt), 0, chan=self.qubit_info.sideband_channels[0])]),
#                                   Join([Constant(int(dt), 0, chan=self.cavity_info.sideband_channels[0]),
#                                         grape_c])
#                        ]))
            elif dt == 0:
                s.append(Combined([grape_t,grape_c]))
#            s.append(r_p(np.pi, X_AXIS))

            s.append(r_p(np.pi/2, X_AXIS))
            s.append(Delay(self.t_ge))
            s.append(r_p(-np.pi/2, X_AXIS))

            if self.postseq:
                s.append(self.postseq)
                
            s.append(Combined([Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                               Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
            s.append(Delay(2000))
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs
#    
#    def generate_new(self):
#        s = Sequence()
#        r_a4 = self.qubit_a4.rotate_selective
#        for dt in self.rel_delays:
#            s.append(self.seq)
#            if dt < 0:
#                s.append(Combined([CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_transmon_1000ns.csv', 
#                                       44, chan=self.qubit_info.sideband_channels[0], pre_delay = 0, post_delay = -dt),
#                              CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_cavity_1000ns.csv', 
#                                       144, chan=self.cavity_info.sideband_channels[0], pre_delay = -dt, post_delay = 0)
#                    ]))
#            elif dt > 0:
#                s.append(Combined([CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_transmon_1000ns.csv', 
#                                       44, chan=self.qubit_info.sideband_channels[0], pre_delay = dt, post_delay = 0),
#                              CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_cavity_1000ns.csv', 
#                                       144, chan=self.cavity_info.sideband_channels[0], pre_delay = 0, post_delay = dt)
#                    ]))
#            elif dt == 0:
#                s.append(Combined([CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_transmon_1000ns.csv', 
#                                           44, chan=self.qubit_info.sideband_channels[0]),
#                                  CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_cavity_1000ns.csv', 
#                                           144, chan=self.cavity_info.sideband_channels[0])
#                        ]))
#            s.append(r_a4(np.pi, X_AXIS))
#
#            if self.postseq:
#                s.append(self.postseq)
#            s.append(Combined([Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                               Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                    ]))
#            s.append(Delay(2000))
#        s = self.get_sequencer(s)
#        seqs = s.render()
#        return seqs
    
#    def generate(self):
#        s = Sequence()
#        r_a4 = self.qubit_a4.rotate_selective
#        for dt in self.rel_delays:
#            s.append(self.seq)
#            d1 = dt * (np.sign(dt) + 1)/2
#            d2 = np.abs(dt-d1)
#            t_seq = CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_transmon_1000ns.csv', 
#                                       44, chan=self.qubit_info.sideband_channels[0], pre_delay = d1, post_delay = d2)
#            c_seq = CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_cavity_1000ns.csv', 
#                                       144, chan=self.cavity_info.sideband_channels[0], pre_delay = d2, post_delay = d1)
#            print(t_seq.get_length(), c_seq.get_length())
#            
#            s.append(Combined([t_seq, c_seq]))
##            s.append(Combined([CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_transmon_1000ns.csv', 
##                                       44, chan=self.qubit_info.sideband_channels[0], pre_delay = d1, post_delay = d2),
##                              CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_cavity_1000ns.csv', 
##                                       144, chan=self.cavity_info.sideband_channels[0], pre_delay = d2, post_delay = d1)
##                    ]))
#            s.append(r_a4(np.pi, X_AXIS))
#
#            if self.postseq:
#                s.append(self.postseq)
#            s.append(Combined([Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                               Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                    ]))
#            s.append(Delay(2000))
#        s = self.get_sequencer(s)
#        seqs = s.render()
#        return seqs

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
        self.fig = fig

