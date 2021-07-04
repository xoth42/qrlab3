# -*- coding: utf-8 -*-
"""
Created on Sat May 29 18:42:12 2021

@author: wanglab
"""


import numpy as np
from instrumentserver.visainstrument import VisaInstrument
from .instrument import Instrument
import types
import logging
class YokoException(Exception):
    pass
class SignalHound_Spike(VisaInstrument):
    """
    Communication with Spike software to control the spectrum analyzer
    """

    def __init__(self, name, address, **kwargs):
        super(SignalHound_Spike, self).__init__(name, address=address, term_chars='\n', **kwargs)
        
        self._modes = {0: 'SA', 1: 'RTSA', 2: 'ZS', 3: 'HARM', 4: 'SCAL', 5: 'PN', 
                       6: 'DDEMOD', 7: 'EMI', 8: 'ADEMOD', 9: 'IH', 10: 'SEM'}

    def do_get_marker_XY(self):
        """
        Get selected marker X (frequency in Hz) and Y (amplitude in dBm) position
        """
        X = float(self.ask(':CALC:MARK:X?'))
        Y = float(self.ask(':CALC:MARK:Y?'))
        return X,Y
    
    def do_set_marker_X(self, X):
        """
        Set marker X position (frequency, in Hz)
        """
        self.write(':CALC:MARK:X %s' % X)
        
    def do_set_marker_peaktracing(self, peaktracing):
        if peaktracing:
            peaktracing = 'ON'
        else:
            peaktracing = 'OFF'
        
        self.write(':CALC:MARK:PKTR %s' % peaktracing)
        
        
    def do_set_mode(self, mode):
       
       if isinstance(mode, int):
           mode = self_modes[mode]
      
       self.write(':INST:SEL ' + mode)
       
    def do_set_center_frequency(self, center):
       self.write(':SENS:FREQ:CENTER %s' % center)
          
    
if __name__ == '__main__':
    
    if spike:
        spike.close()
    spike = SignalHound_Spike('Spike', 'TCPIP::localhost::5025::SOCKET')
    
    spike.do_set_marker_X(1.1e9)
    
    print((spike.do_get_marker_XY()))