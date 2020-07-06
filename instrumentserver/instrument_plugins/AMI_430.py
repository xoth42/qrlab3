# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 11:11:02 2018

@author: WangLab2
"""

import types
import objectsharer as objsh

from instrument import Instrument

import serial

class AMI_430(Instrument):
    def __init__(self, name, **kwargs):
        super(AMI_430, self).__init__(name)
        
        self.ser = serial.Serial('COM8', 
                                 baudrate= 115200, 
                                 parity=serial.PARITY_NONE, 
                                 stopbits= serial.STOPBITS_ONE, 
                                 bytesize= serial.EIGHTBITS,
                                 timeout= 10,
                                 rtscts=True)

        #self.ser.open() # this line may be uneccessary
        self._max_field = 4 #TBD
        self._min_field = 0 #TBD
        self._max_current = 100 #TBD
        self._min_current = 0 #TBD
        self.field = 0
        self.current = 0
    
        self.add_parameter('field', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='Tesla',
            minval=self._min_field, maxval=self._max_field,
            format='%.04f') #format may need to be adjusted based on units
        
        self.add_parameter('Current', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='Amps',
            minval=self._min_current, maxval=self._max_current,
            format='%.04f') #format may need to be adjusted 
        
        
    def do_get_field(self):
        self.ser.write('FIELD:MAGnet?;')
        self.field = self.ser.read(size=20) #size TBD

        return self.field
    
    def do_set_field(self, field):
        self.field = field
        self.ser.write('CONFigure:FIELD:TARGet %s;'%(field)) #sets field target
        self.ser.write('RAMP;') #tells magnet to go to the target
#        try:
#            while not abs(float(self.do_get_field()) - field) < 0.0005:
#
#                objsh.helper.backend.main_loop(100)
#
#        except:
#            print 'error in ramping field'
    
    def do_get_current(self):
        self.ser.write('CURRent:MAGnet?;')
        self.current = self.ser.read(size=20) #size TBD
        return self.current
        
    def do_set_current(self, current):
        self.current = current
        self.ser.write('CONFigure:CURRent:TARGet %s;'%(current)) #sets current target
        self.ser.write('RAMP;') #tells magnet to go to the target
    
    def do_pause(self):
        self.ser.write('PAUSE;') #pause the ramping 
        
    def do_ramp_zero(self):
        self.ser.write('ZERO;') #puts the programmer into zeroing current mode'''
        
    def do_set_PSwitch(self,state):
        self.ser.write('PSwitch %s;'%(state))
#        self.ser.write('CONFigure:PSwitch:INSTalled?;')
#        self.PSwitch = self.ser.read(size=20) #size TBD
#
#        return self.PSwitch
         
    def do_get_PSwitch(self):
        self.ser.write('PSwitch?;')
        self.PSwitch = self.ser.read(size = 8)
        
        return self.PSwitch
    
    def do_get_Lock_PSwitch(self):
        self.ser.write('LOCK:PSwitch:CONTRol?;')
        self.Lock_PSwitch = self.ser.read(size = 8)
        
        return self.Lock_PSwitch
        
    def IDN(self):
        self.ser.write('*IDN?;')
        self.IDN = self.ser.read(size = 20)
        
        return self.IDN
