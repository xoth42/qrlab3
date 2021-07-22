# -*- coding: utf-8 -*-
"""
Created on Tue May 26 12:57:00 2020

@author: Wang_Lab
"""
import sys
import time
import types


from instrument import Instrument
from windfreak import SynthHD

# Please check what COM-port you have the windfreak connected to and then change self.synth in line 21

class WFT1153(Instrument):
    
    
    def __init__(self, name, channel_index = None, COM_adrs='COM3', serial=None):
        self.synth = SynthHD(COM_adrs)


        self.channel_index = channel_index
        
        super(WFT1153, self).__init__(name)
        if serial is None:
            raise Exception('Windfreak driver needs serial as parameter')
        
        
        # Added by Tal on 07/21/21.
        # If channel_index is not specified, the GUI will create both channels, 
        #if channel_index is specified it will create only the requested channel.
        
        if self.channel_index==None: 
            for channel in range(2):
                print((channel))
                print((self.synth[channel].frequency))
                self._min_freq = 10e6
                self._max_freq = 15000e6
                self._min_power = -70.
                self._max_power = 20.
                
                self.add_parameter('frequency', type=float,
                                    flags=Instrument.FLAG_GETSET, units='Hz',
                                    minval=self._min_freq, maxval=self._max_freq,
                                    display_scale=6, value = self.synth[channel].frequency, 
                                    channels = [channel + 1])
                
                self.add_parameter('power', type=float,
                                    flags=Instrument.FLAG_GETSET, units='dBm',
                                    minval=self._min_power, maxval=self._max_power,
                                    format='%.02f', value = self.synth[channel].power,
                                    channels = [channel + 1])
                
                self.add_parameter('rf_on', type=bool,
                                    flags=Instrument.FLAG_GETSET, value = self.synth[channel].enable,
                                    channels = [channel + 1])
        
        else:    
            print((self.channel_index))
            print((self.synth[self.channel_index].frequency))
            self._min_freq = 10e6
            self._max_freq = 15000e6
            self._min_power = -70.
            self._max_power = 20.
            
            self.add_parameter('frequency', type=float,
                flags=Instrument.FLAG_GETSET, units='Hz',
                minval=self._min_freq, maxval=self._max_freq,
                display_scale=6, value = self.synth[self.channel_index].frequency, 
                channels = self.channel_index)
            
            self.add_parameter('power', type=float,
                flags=Instrument.FLAG_GETSET, units='dBm',
                minval=self._min_power, maxval=self._max_power,
                format='%.02f', value = self.synth[self.channel_index].power,
                channels = self.channel_index)
            
            self.add_parameter('rf_on', type=bool,
                flags=Instrument.FLAG_GETSET, value = self.synth[self.channel_index].enable,
                channels = self.channel_index)
            
        
     
    def do_get_frequency(self, index=None):
        if index is None: index = self.channel_index
        return self.synth[index].frequency
        
    
    def do_set_frequency(self, value, index=None):
        if index is None: index = self.channel_index
        self.synth[index].frequency = value
        return self.synth[index].frequency
         
        
    def do_get_power(self, index=None):
        if index is None: index = self.channel_index
        return self.synth[index].power
        
    def do_set_power(self, value, index=None):
        if index is None: index = self.channel_index
        self.synth[index].power = value
        return self.synth[index].power 
        
        
    def do_get_rf_on(self, index=None):
        if index is None: index = self.channel_index
        return self.synth[index].enable==True
    
    def do_set_rf_on(self, val, index=None):
        if index is None: index = self.channel_index
        if(val):
            self.synth[index].enable=True
            return self.synth[index].enable
        else:
            self.synth[index].enable=False
            return self.synth[index].enable


            
       
    
    
    
    
    
    
    
    
    
    
    
    