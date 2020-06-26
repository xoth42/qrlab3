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

synth = SynthHD('COM10')
    

channel_index = 0 #using the RF A port on windfreak

class WFT1243(Instrument):
    
    
    def __init__(self, name, serial=None):
        super(WFT1243, self).__init__(name)
        if serial is None:
            raise Exception('Windfreak driver needs serial as parameter')
        
         
        
        
        self._min_freq = 10.e6
        self._max_freq = 15000.e6
        self._min_power = -70.
        self._max_power = 20.
        
        self.add_parameter('frequency', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='Hz',
            minval=self._min_freq, maxval=self._max_freq,
            display_scale=6, value = synth[channel_index].frequency)
        
        self.add_parameter('power', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='dBm',
            minval=self._min_power, maxval=self._max_power,
            format='%.02f', value = synth[channel_index].power)
        
        self.add_parameter('rf_on', type=types.BooleanType,
            flags=Instrument.FLAG_GETSET, value = synth[channel_index].enable)
        
        
        
    def do_get_frequency(self):
        return synth[channel_index].frequency
        
    
    def do_set_frequency(self, value):
        synth[channel_index].frequency = value
        return synth[channel_index].frequency
         
        
    
    def do_get_power(self):
        return synth[channel_index].power
        
    def do_set_power(self, value):
        synth[channel_index].power = value
        return synth[channel_index].power 
        
        
    def do_get_rf_on(self):
        return synth[channel_index].enable==True
    
    def do_set_rf_on(self, val):
        if(val):
            synth[channel_index].enable=True
            return synth[channel_index].enable
        else:
            synth[channel_index].enable=False
            return synth[channel_index].enable
            

            
       
    
    
    
    
    
    
    
    
    
    
    
    