# -*- coding: utf-8 -*-
"""
Created on Thu Oct 05 12:14:26 2017

@author: Wanglab
"""

import types

from instrument import Instrument

from PyMata.pymata import PyMata

class Magnet_power_supply(Instrument):
   
    def __init__(self, name, adrs= None, **kwargs):
        super(Magnet_power_supply, self).__init__(name)
        
        self._max_field = 400
        self._min_field = 0
        self.field= 0
        
        self.add_parameter('field', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='mT',
            minval=self._min_field, maxval=self._max_field,
            format='%.01f')
        
    def _init(self):
        board = PyMata(port_id = 'COM3')
            
        board.i2c_config(pin_type='ANALOG',clk_pin=5, data_pin=4)
            
    def do_set_field(self, Field):
        self.field = Field
        Field = int(Field * 4095/400)
        vala = (Field)/256
        valb = Field-(256*vala)
        board.i2c_write(self.adrs,vala,valb)
        return self.field  
        
    def do_get_field(self):
        return self.field
    
    
    def do_get_max_field(self):
        return self._max_field
    
    def do_get_min_field(self):
        return self._min_field