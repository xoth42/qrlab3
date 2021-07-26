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

def analysis(powers, freqs, realdata, imagdata, fig_name, full_fig_name, Sij, fig=None):
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
        
    powers = np.concatenate((powers, np.zeros(1) + powers[-1]-powers[-2] + powers[-1]))
    ampdata = np.zeros((len(Sij),len(powers), len(freqs[0])))
    ampdata_a = np.zeros((len(Sij),len(freqs[0]), len(powers)))
    xs,ys = np.meshgrid(powers, freqs[0])
    ys = np.zeros((len(powers), len(freqs[0])))
    for i in range(len(powers)-1):
        ys[i] = freqs[i]
    ys[len(powers)-1] = freqs[-1]
    ys = np.transpose(ys)
    gss=[0,0,0,0]
    for k in range(len(Sij)):
    #    if not len(Sij) == 1:
        gss[k] = gridspec.GridSpecFromSubplotSpec(1,2, subplot_spec=gs[k],width_ratios = (19,1))        
        fig.add_subplot(gss[k][0])
        fig.axes[k].set_title('%s%s'%(fig_name,Sij[k]))
        fig.axes[k].set_xlim(xs.min(), xs.max())
        fig.axes[k].set_ylim(ys.min(), ys.max())
        
    #        ampdata = np.zeros((len(realdata),len(powerdata[0,:]), len(freqdata[0,:])))
    #    imag = np.zeros((len(self.powers),len(self.freqs)))
        for i in range(len(powers)-1):
            ampdata[k][i] = 20*np.log10(np.sqrt(realdata[k][i,:]**2 + imagdata[k][i,:]**2))
            
#        ampdata[k][len(powers)-1] = 20*np.log10(np.sqrt(realdata[k][i,:]**2 + imagdata[k][i,:]**2))
    #    print Z
        ampdata_a[k] = np.transpose(ampdata[k])
    #    print ampdata_a[k]
    #    phase = np.transpose(phase)
        a[k]=fig.axes[k].pcolormesh(xs, ys, ampdata_a[k])
    #    Colorbar(ax = fig.axes[k], mappable = a, orientation = 'horizontal', ticklocation = 'top')
    #    pl.colorbar( a[k] )#, ax = gs[k/2, k%2] )
        fig.axes[k].set_xlabel('powers(dB)')
        fig.axes[k].set_ylabel('Frequency(GHz)')
    
    
    for k in range(len(Sij)):
        fig.add_subplot(gss[k][1])
        pl.colorbar( a[k],fig.axes[len(Sij)+k])
        
    pl.suptitle(full_fig_name)
    if fn is None:
        fn = os.path.join(config.datadir, 'images/%s_Power_Sweep_VNA.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    fig.savefig(fn, **kwargs)

class Power_Sweep_Varies_freq_VNA(Measurement1D):

    def __init__(self, powers, center_freqs, span, VNA_points, average_factor,avelimit,if_bandwidth, Sij, fig_name, comment, **kwargs):
        self.powers = powers
#        print 'self.powers', self.powers
        self.center_freqs = center_freqs
        self.average_factor = average_factor
        self.span = span
        self.VNA_points = VNA_points
        self.avelimit = avelimit
        self.if_bandwidth = if_bandwidth
        self.Sij = Sij
        self.fig_name = fig_name
        self.comment = comment
        self.dpowers = powers[-1] - powers[-2]
#        self.sleeptime_field = sleeptime_field
#        self.plot_type = plot_type
#
        super(Power_Sweep_Varies_freq_VNA, self).__init__(1, **kwargs)
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
        print(self.data.get_fullname())
        self.full_fig_name = self.data.get_fullname()
        self.powerdata = self.data.create_dataset('powers', data=self.powers)
        self.freqs = self.data.create_dataset('freqs', shape=[len(self.powers),self.VNA_points])
        
    
#        self.powerdata = self.data.create_dataset('powers', shape=[1,len(self.powers)])
#        self.freqdata = self.data.create_dataset('freqs', shape=[1,len(self.freqs)])
##        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(self.powers),len(freqs)])
##        self.phasedata = self.data.create_dataset('phases', shape=[len(self.powers),len(freqs)])
#        print self.freqdata.get_fullname()
        self.realdata = [0,0,0,0]
        self.imagdata = [0,0,0,0]
        for i, sij in enumerate(self.Sij):
            
            self.realdata[i] = self.data.create_dataset('real%s'%(sij), shape=[len(self.powers),self.VNA_points])
            self.imagdata[i]= self.data.create_dataset('imaginary%s'%(sij), shape=[len(self.powers),self.VNA_points])
#        
        
    def measure(self):
        # Generate and load sequences
        VNA = self.instruments['VNA']
#        Yoko = self.instruments['Yoko']
        SCqubit = self.instruments['SCqubit']

        VNA.set_s_param(self.Sij[0])
        VNA.set_span(self.span)
        VNA.set_points(self.VNA_points)
        Freqs = VNA.do_get_xaxis()

#            break
#        self.freqdata[0,:] = Freqs
#        self.powerdata[0,:] = self.powers
        
        xs,ys = np.meshgrid(self.powers, self.freqs[0])
#        timelimit = 16 # breaks long time measurement to severals 16 seconds.
#        avelimit = int(timelimit/VNA.get_sweep_time())
        avelimit = self.avelimit
        if avelimit<1:
            avelimit = 1
        if avelimit >999:
            avelimit = 999
            
        if self.average_factor < avelimit:
            avelimit = self.average_factor
            
        VNA.set_average_factor(avelimit)
        VNA.set_if_bandwidth(self.if_bandwidth)
        
        for ipower, power in enumerate(self.powers):
#            VNA.set_power(power)
#            if power == -14:
#                SCqubit.set_rf_on(False)
#            else:
#                SCqubit.set_rf_on(True)                
#            SCqubit.set_power(power)
#            self.powerdata[ipower] = SCqubit.get_power()
            self.powerdata[ipower] = power
            
            
            VNA.set_center_freq(self.center_freqs[ipower])
#            time.sleep(0.5)
            ave = avelimit
            
            if self.average_factor > avelimit:
                VNA.set_average_factor(ave)
            count = 0
            
            Freqs = VNA.do_get_xaxis()
            self.freqs[ipower,:] = Freqs
            
            while count < self.average_factor:
                ave = avelimit
                
                if (self.average_factor-count) < avelimit:
                    ave = self.average_factor-count
                    VNA.set_average_factor(ave)
                
#                reals = []
#                imags = []
        
        
    #            VNA.set_trigger_source('internal')
    #            VNA.set_average_factor(40)
    
                VNA.set_trigger_source('BUS')
#                VNA.write('INIT:CONT ON')
        
#                VNA.set_averaging_trigger(1)
                VNA.trigger()
                
                wait = VNA.opc(async_=True) # wait for completion
        
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
                    print('error with async')
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
                        self.realdata[i][ipower,:] = reals
                        self.imagdata[i][ipower,:] = imags
            
                    else:
                        reals =( reals *ave + self.realdata[i][ipower,:] * count)/float(ave+count)
                        imags =( imags *ave + self.imagdata[i][ipower,:] * count)/float(ave+count)
                        self.realdata[i][ipower,:] = reals
                        self.imagdata[i][ipower,:] = imags
    
    
                VNA.set_trigger_source('internal')
                count = count + ave
                print('%s averages done' %(count))
            
            print('power = %.04fdB done  %s/%s' % (power, ipower+1, len(self.powers)))
            if ipower == 0:
                self.fig = pl.figure()
                if len(self.Sij) == 1:
                    gs = gridspec.GridSpec(1, 1)
        #            fig.axes[0].title = Sij[0]
                else:
                    gs = gridspec.GridSpec((len(self.Sij)-1)/2 + 1, 2)
                    gs.update(wspace=0.4, hspace=0.35)
                for i in range(len(self.Sij)):
                    self.fig.add_subplot(gs[i])
                    self.fig.axes[i].set_title('%s%s'%(self.fig_name,self.Sij[i]))
                    self.fig.axes[i].set_xlim(xs.min(), xs.max()+self.dpowers)
#                    self.fig.axes[i].set_ylim(ys.min(), ys.max())
                    
                pl.suptitle(self.full_fig_name)
        
            for i in range(len(self.Sij)):
                z1 = 20*np.log10(self.realdata[i][ipower,:]**2 + self.imagdata[i][ipower,:]**2)
                z1 = z1[:,None].T
                z2 = 20*np.log10(self.realdata[i][ipower,:]**2 + self.imagdata[i][ipower,:]**2)
                z2 = z2[:,None].T
                z = np.concatenate([z1,z2])
                z = np.transpose(z)
                x = np.zeros((len(self.freqs[ipower]),2))
                x[:,0] = self.powers[ipower]
                x[:,1] = self.powers[ipower]+self.dpowers
                y = np.zeros((2,len(self.freqs[ipower])))
                y[0] = y[1] = self.freqs[ipower]
                y = np.transpose(y)
                self.fig.axes[i].pcolormesh(x, y, z,vmax=np.max(z))#,vmin = np.max([np.min(z),-200]))
                print(np.max(z), np.min(z))
        #        fig.axes[i].set_xlim(xs.min(), xs.max())
        #        fig.axes[i].set_ylim(ys.min(), ys.max())
                self.fig.canvas.draw()

#        print 'self.freqs\n', self.freqs.value
        self.analyze()
        print(self.data.get_fullname())
        
    def analyze(self):
        analysis(self.powers, self.freqs, self.realdata, self.imagdata, self.fig_name,self.full_fig_name, self.Sij, fig = None)
