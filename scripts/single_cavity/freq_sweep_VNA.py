# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 10:44:46 2020

@author: WangLab
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 17:59:45 2019

@author: Wang_Lab
"""

#import mclient
from measurement import Measurement1D
import matplotlib.pyplot as pl
#from pulseseq.sequencer import *
#from pulseseq.pulselib import *
from lib.math import fit
import objectsharer as objsh
import time
import numpy as np
from matplotlib import gridspec
import os
import config
#
#SPEC   = 0
#POWER  = 1

# creates plot
def analysis(drive_freqs, freqs, realdata, imagdata, fig_name, full_fig_name, Sij, fig=None):
    fn = None
    fig = pl.figure()
    a=[0,0,0,0]
    
    if len(Sij) == 1:
    #    gs=[0]
        gs= gridspec.GridSpec(1 , 1)
    #            fig.axes[0].title = Sij[0]
    else:
        gs = gridspec.GridSpec((len(Sij)-1)/2 + 1, 2)
        gs.update(wspace=0.5, hspace=0.4)
        
    drive_freqs = np.concatenate((drive_freqs, np.zeros(1) + drive_freqs[1]-drive_freqs[0] + drive_freqs[-1]))
    ampdata = np.zeros((len(Sij),len(drive_freqs), len(freqs)))
    ampdata_a = np.zeros((len(Sij),len(freqs), len(drive_freqs)))
    xs,ys = np.meshgrid(drive_freqs/float(1e9), freqs/float(1e9))
    gss=[0,0,0,0]
    for k in range(len(Sij)):
    #    if not len(Sij) == 1:
        gss[k] = gridspec.GridSpecFromSubplotSpec(1,2, subplot_spec=gs[k],width_ratios = (19,1))        
        fig.add_subplot(gss[k][0])
        fig.axes[k].set_title('%s'%(fig_name))
        fig.axes[k].set_xlim(xs.min(), xs.max())
        fig.axes[k].set_ylim(ys.min(), ys.max())
        
    #        ampdata = np.zeros((len(realdata),len(drive_freqdata[0,:]), len(freqdata[0,:])))
    #    imag = np.zeros((len(self.drive_freqs),len(self.freqs)))
        for i in range(len(drive_freqs)-1):
            ampdata[k][i] = 20*np.log10(np.sqrt(realdata[k][i,:]**2 + imagdata[k][i,:]**2))
            
        ampdata[k][len(drive_freqs)-1] = 20*np.log10(np.sqrt(realdata[k][i,:]**2 + imagdata[k][i,:]**2))
    #    print Z
        ampdata_a[k] = np.transpose(ampdata[k])
    #    print ampdata_a[k]
    #    phase = np.transpose(phase)
        a[k]=fig.axes[k].pcolormesh(xs, ys, ampdata_a[k])
    #    Colorbar(ax = fig.axes[k], mappable = a, orientation = 'horizontal', ticklocation = 'top')
    #    pl.colorbar( a[k] )#, ax = gs[k/2, k%2] )
        fig.axes[k].set_xlabel('drive_freqs(GHz)')
        fig.axes[k].set_ylabel('Frequency(GHz)')
    
    
    for k in range(len(Sij)):
        fig.add_subplot(gss[k][1])
        pl.colorbar( a[k],fig.axes[len(Sij)+k])
        
    pl.suptitle(full_fig_name)
    if fn is None:
        fn = os.path.join(config.datadir, 'images/%s_Freq_Sweep_VNA.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    fig.savefig(fn, **kwargs)

class Freq_Sweep_VNA(Measurement1D):

    def __init__(self,drive, drive_freqs, freqs, average_factor,avelimit,if_bandwidth, Sij, fig_name,comment, **kwargs):
        self.drive = drive
        self.drive_freqs = drive_freqs
#        print 'self.drive_freqs', self.drive_freqs
        self.freqs = freqs
        self.average_factor = average_factor
        self.avelimit = avelimit
        self.if_bandwidth = if_bandwidth
        self.Sij = Sij
        self.fig_name = fig_name
        self.comment = comment
        self.ddrive_freqs = drive_freqs[1] - drive_freqs[0]
#        self.sleeptime_field = sleeptime_field
#        self.plot_type = plot_type
#
        super(Freq_Sweep_VNA, self).__init__(1, **kwargs)
#        self.set_attrs(
#            title=self.fig_name,
#            comment=self.comment,
#            Sij_list = self.Sij,
#            VNA_IF_bandwidth = if_bandwidth,
#            total_average_factor = average_factor,
#            mainlooptime = 100,
#            stop_at = '0/%s'%(len(self.powers)),
#            avelimit = self.avelimit,   
#        )
        print self.data.get_fullname()
        self.full_fig_name = self.data.get_fullname()
        self.data.create_dataset('drive_freqs', data=self.drive_freqs)
        self.data.create_dataset('freqs', data=self.freqs)
        
    
#        self.drive_freqdata = self.data.create_dataset('drive_freqs', shape=[1,len(self.drive_freqs)])
#        self.freqdata = self.data.create_dataset('freqs', shape=[1,len(self.freqs)])
##        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(self.drive_freqs),len(freqs)])
##        self.phasedata = self.data.create_dataset('phases', shape=[len(self.drive_freqs),len(freqs)])
#        print self.freqdata.get_fullname()
        self.realdata = [0,0,0,0]
        self.imagdata = [0,0,0,0]
        for i, sij in enumerate(self.Sij):
            
            self.realdata[i] = self.data.create_dataset('real%s'%(sij), shape=[len(self.drive_freqs),len(freqs)])
            self.imagdata[i]= self.data.create_dataset('imaginary%s'%(sij), shape=[len(self.drive_freqs),len(freqs)])
#        
        
    def measure(self):
        # Generate and load sequences
        VNA = self.instruments['VNA']
#        Yoko = self.instruments['Yoko']
#        SC = self.instruments['SC_qubit2FWM']
#        brick2 = self.instruments['brick2']
#        brick3 = self.instruments['brick3']

        VNA.set_start_freq(self.freqs[0])
        VNA.set_stop_freq(self.freqs[-1])
        VNA.set_points(len(self.freqs))
        VNA.set_s_param(self.Sij[0])
        Freqs = VNA.do_get_xaxis()
        if not (Freqs == self.freqs).all():
            print 'error in setting frequency'
#            break
#        self.freqdata[0,:] = Freqs
#        self.drive_freqdata[0,:] = self.drive_freqs
        
        xs,ys = np.meshgrid(self.drive_freqs, self.freqs)
#        timelimit = 16 # breaks long time measurement to severals 16 seconds.
#        avelimit = int(timelimit/VNA.get_sweep_time())
        avelimit = self.avelimit
        if avelimit<1:
            avelimit = 1
        if avelimit >999:
            avelimit = 999
            
            
#        VNA.set_average_factor(avelimit)
        VNA.set_if_bandwidth(self.if_bandwidth)
        
        for idrive_freq, drive_freq in enumerate(self.drive_freqs):
            avelimit = self.avelimit
#            brick3.set_power(power)
#            SC.set_power(power)
#            VNA.set_power(power)
            self.drive.set_frequency(drive_freq)
#            if power == -31:
#                SCqubit.set_rf_on(False)
#            else:
#                SCqubit.set_rf_on(True)                
#            brick2.set_frequency(power)
            time.sleep(10)
            if self.average_factor[idrive_freq] < avelimit:
                avelimit = self.average_factor[idrive_freq]
            ave = avelimit
            VNA.set_average_factor(avelimit)
#            if self.average_factor[idrive_freq] > avelimit:
#                VNA.set_average_factor(ave)
            count = 0
    
            while count < self.average_factor[idrive_freq]:
                ave = avelimit
                
                if (self.average_factor[idrive_freq]-count) < avelimit:
                    ave = self.average_factor[idrive_freq]-count
                    VNA.set_average_factor(ave)
                
#                reals = []
#                imags = []
        
        
    #            VNA.set_trigger_source('internal')
    #            VNA.set_average_factor(40)
    
                VNA.set_trigger_source('BUS')
#                VNA.write('INIT:CONT ON')
        
#                VNA.set_averaging_trigger(1)
                VNA.trigger()
                
                wait = VNA.opc(async=True) # wait for completion
        
    #            print 'ok7'
#                a=0
                try:
                    while not wait.is_valid():
#                        if a % 10 == 0:
#                            print 'async', a 
#                        a= a + 1
                        
    #                    time.sleep(0.1)
                        objsh.helper.backend.main_loop(100)
                        VNA.set_format('MLOG')
                except:
                    print 'error with async'
    #                VNA.set_interrupt(True)
    #        '''
        
    #            print 'ok8'
                for i, sij in enumerate(self.Sij):
                    if len(self.Sij) > 1:  
                        VNA.set_s_param(sij)
#                    prev_fmt = VNA.get_format()
#                    freqs = VNA.do_get_xaxis()
                    VNA.set_format('REAL')
                    ret = VNA.do_get_yaxes()
                    reals = ret[0]
                    VNA.set_format('IMAG')
                    ret = VNA.do_get_yaxes()
                    imags = ret[0]
                    VNA.set_format('MLOG')
                
        #        ret = VNA.do_get_data()
#                VNA.set_trigger_source('internal')
        #        amps=ret[0]
        #        phases=ret[1]
        #        print 'F = %.03f GHz --> amp = %.1f, angle = %.01f' % (freq / 1e9, np.abs(IQ), np.angle(IQ, deg=True))
        
                    if count == 0:
                        
    #                    self.freqdata[0,:] = freqs
                #        print freqs
                #        print self.freqdata
                        self.realdata[i][idrive_freq,:] = reals
                        self.imagdata[i][idrive_freq,:] = imags
            
            
                    else:
                        reals =( reals *ave + self.realdata[i][idrive_freq,:] * count)/float(ave+count)
                        imags =( imags *ave + self.imagdata[i][idrive_freq,:] * count)/float(ave+count)
                        self.realdata[i][idrive_freq,:] = reals
                        self.imagdata[i][idrive_freq,:] = imags
    
    
                VNA.set_trigger_source('internal')
                count = count + ave
                print '%s averages done' %(count)
            
            print 'drive_freq = %.04fGHz done ' % (drive_freq)
            if idrive_freq == 0:
                self.fig = pl.figure()
                if len(self.Sij) == 1:
                    gs = gridspec.GridSpec(1, 1)
        #            fig.axes[0].title = Sij[0]
                else:
                    gs = gridspec.GridSpec((len(self.Sij)-1)/2 + 1, 2)
                    gs.update(wspace=0.4, hspace=0.35)
                for i in range(len(self.Sij)):
                    self.fig.add_subplot(gs[i])
                    self.fig.axes[i].set_title('%s'%(self.fig_name))
                    self.fig.axes[i].set_xlim(xs.min(), xs.max()+self.ddrive_freqs)
                    self.fig.axes[i].set_ylim(ys.min(), ys.max())
        
            for i in range(len(self.Sij)):
                z1 = 20*np.log10(self.realdata[i][idrive_freq,:]**2 + self.imagdata[i][idrive_freq,:]**2)
                z1 = z1[:,None].T
                z2 = 20*np.log10(self.realdata[i][idrive_freq,:]**2 + self.imagdata[i][idrive_freq,:]**2)
                z2 = z2[:,None].T
                z = np.concatenate([z1,z2])
                z = np.transpose(z)
                x = np.zeros((len(self.freqs),2))
                x[:,0] = self.drive_freqs[idrive_freq]
                x[:,1] = self.drive_freqs[idrive_freq]+self.ddrive_freqs
                y = np.zeros((2,len(self.freqs)))
                y[0] = y[1] = self.freqs
                y = np.transpose(y)
                self.fig.axes[i].pcolormesh(x, y, z,vmax=np.max(z))#,vmin = np.max([np.min(z),-200]))
                print np.max(z), np.min(z)
        #        fig.axes[i].set_xlim(xs.min(), xs.max())
        #        fig.axes[i].set_ylim(ys.min(), ys.max())
                self.fig.canvas.draw()

#        print 'self.ampdata\n', self.ampdata
        pl.close()
        self.analyze()
        print self.data.get_fullname()
        
    def analyze(self):
        analysis(self.drive_freqs, self.freqs, self.realdata, self.imagdata, self.fig_name,self.full_fig_name, self.Sij, fig = None)
