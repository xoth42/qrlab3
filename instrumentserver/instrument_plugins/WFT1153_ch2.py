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
import WFT1153 as ref    


class WFT1153_ch2(Instrument):
    
    
    def __init__(self, name, ins_name=None, channel_index = 1):
#        super(WFT1153_ch2, self).__init__(name)
        Instrument.__init__(self, name, tags=['virtual'])
        
#        srv = self.get_instruments()
        
#        if srv:
#            self._ins = srv.get(ins_name)
        
        

        self.channel_index = channel_index
        #self.reference = reference

        


        print(self.channel_index)
        self._min_freq = 10.e6
        self._max_freq = 15000.e6
        self._min_power = -70.
        self._max_power = 20.
        
        
        self.add_parameter('frequency', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='Hz',
            minval=self._min_freq, maxval=self._max_freq,
            display_scale=6, 
            value = self._min_freq)
        
        self.add_parameter('power', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='dBm',
            minval=self._min_power, maxval=self._max_power,
            format='%.02f', 
            value = self._min_power)
        
        self.add_parameter('rf_on', type=types.BooleanType,
            flags=Instrument.FLAG_GETSET, 
            value = False)
        
    
    def do_set_rfsource(self, val):
        srv = self.get_instruments()
        if srv:
            self._ins = srv.get(val)
        else:
            self._ins = None        

     
    def do_get_frequency(self):
        return self._ins.do_get_frequency(index=self.channel_index)
        
    
    def do_set_frequency(self, value):
        return self._ins.do_set_frequency(value, index=self.channel_index)
        
    
    def do_get_power(self):
        return self._ins.do_get_power(index=self.channel_index)
        
    def do_set_power(self, value):
        return self._ins.do_set_power(value, index=self.channel_index)

    def do_get_rf_on(self):
        return self._ins.do_get_rf_on(index=self.channel_index)
    
    def do_set_rf_on(self, value):
        return self._ins.do_set_rf_on(value, index=self.channel_index)


            
       
    
    
    
    
    
    
    
    
    
    
    
    