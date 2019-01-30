from measurement import Measurement1D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import objectsharer as objsh
import time
#
#SPEC   = 0
#POWER  = 1



class SingleTrace(Measurement1D):

    def __init__(self,freqs, use_async, **kwargs):
        self.freqs =freqs
#        self.meas_info = meas_info
#        self.device_info = device_info
#        plot_type = SPEC
        self.use_async = use_async
#        self.plot_type = plot_type

        super(SingleTrace, self).__init__(1, **kwargs)
        self.data.create_dataset('freqs', data=self.freqs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(self.freqs)])
        self.phasedata = self.data.create_dataset('phases', shape=[len(self.freqs)])



    def measure(self):
        # Generate and load sequences
        VNA = self.instruments['VNA']

        if self.use_async:
            VNA.set_start_freq(self.freqs[0])
            VNA.set_stop_freq(self.freqs[-1])
            VNA.set_points(len(self.freqs))
    #        self.freqs = VNA.do_get_xaxis()
    
    
            amps = []
            phases = []
    
    

            VNA.set_trigger_source('BUS')
            VNA.write('INIT:CONT ON')
    
            VNA.set_averaging_trigger(1)
            VNA.trigger()
            ret = VNA.opc(async=True) # wait for completion
    
    #        ret = VNA.do_get_data()
    
    
            try:
                while not ret.is_valid():
                    objsh.helper.backend.main_loop(100)
            except:
                print 'error with async'
    #            VNA.set_interrupt(True)
    

        self.freqs = VNA.do_get_xaxis()
        ret = VNA.do_get_data()
        VNA.set_trigger_source('internal')
#        IQ = np.average(ret.get())
        amps=ret[0]
        phases=ret[1]
#        print 'F = %.03f GHz --> amp = %.1f, angle = %.01f' % (freq / 1e9, np.abs(IQ), np.angle(IQ, deg=True))

        self.ampdata = amps
        self.phasedata = phases

        self.analyze()

    def analyze(self):
        fig = self.create_figure()
        
#        fig.plot(self.freqs, self.ampdata)
#        ax1 = fig.add_subplot(2,1,1)
#        ax2 = fig.add_subplot(2,1,2)

        fig.axes[0].plot(self.freqs/float(1e9), self.ampdata)
        plt.xlabel('freq(GHz)')
        fig.axes[0].set_ylabel('dB')
        
        fig.axes[1].plot(self.freqs/float(1e9), self.phasedata)
#        fig.axes[1].xlabel('freq(GHz)')
        plt.ylabel('phase')
#        analysis(self.freqs, self.ampdata, self.phasedata, self.plot_type, fig=fig)
