# Keithley2200_2400.py class, to perform the communication between the Wrapper and the device
# vishal ranjan, 2012
# Gijs de Lange, 2012
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

## Modified from the Keithley 2200_20_5.py file
## by: Randy
## Added 04/27/2021

from instrument import Instrument
import pyvisa
import types
import logging
import numpy
from time import sleep

class Keithley2400(Instrument):
    '''
    This is the python driver for the Keithley current source

    Usage:
    Initialize with
    <name> = instruments.create('name', 'RS_SMB100', address='<GPIB address>',
        reset=<bool>)
    '''

    def __init__(self, name, address, reset=False):
        super(Keithley2400, self).__init__(name, address=address, term_chars='\r\n')

        '''
        Initializes the Keithley, and communicates with the wrapper.

        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address
            reset (bool)     : resets to default values, default=false

        Output:
            None
        '''

        self._Ires = 0.01
        self._Vres = 0.01

        logging.info(__name__ + ' : Initializing instrument')
#        Instrument.__init__(self, name, tags=['physical'])
        self.rm = pyvisa.ResourceManager()
        self._visainstrument = self.rm.open_resource(address)
        self._address = address
        print ' Keithley timeout set to: %s s'%self._visainstrument.timeout

    # add parameters


        self.add_parameter('status', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('current', type=types.FloatType,
                flags=Instrument.FLAG_GETSET, units = 'Amps')
        
        self.add_parameter('curr_limit', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET, units = 'Amps')

        self.add_parameter('voltage', type=types.FloatType,
                flags=Instrument.FLAG_GETSET, units = 'Volts')


        self.add_function('reset')
        self.add_function('get_all')

        if reset:
            self.reset()
        else:
            self.get_all()


        # add functions here to enable OVP and OCP

    def reset(self):
        '''
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Resetting instrument')
        self._visainstrument.write('*RST')



    def get_all(self):
        '''
        Reads all implemented parameters from the instrument,
        and updates the wrapper.

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : reading all settings from instrument')
#        self.get_channel()
#        self.get_status()
#        self.get_current()




    def do_set_status(self,value):
        '''
        takes value = on/off
            sets the status = on/off
        for the operating channel
        '''


        a= self._visainstrument.write(':OUTP:STAT %s' %(value))

    def do_get_status(self):
        '''
        returns the status = on/off
        for the operating channel
        '''

        return self._visainstrument.query(':OUTP:STAT?').strip()



    def get_visains(self):
        return self._visainstrument


    def do_set_current(self,I):
        '''
        sets the current on the selected channel
        mind the max and min currents

        '''
        ## Set current source, and voltage sense
        self._visainstrument.query(':OUTP OFF;*OPC?')
        self._visainstrument.query(':SOUR:FUNC CURR;*OPC?')
        self._visainstrument.query(':SENS:FUNC "VOLT";*OPC?')
        self._visainstrument.query(':SOUR:CURR:LEV %s;*OPC?' % str(I))
        self._visainstrument.query(':OUTP ON;*OPC?')
        
#        self._ramp_current(I)

    def do_set_curr_limit(self,Imax):
        ## set current limit for a voltage source
        self._visainstrument.write(':SENS:CURR:PROT:LEV %s' % Imax)
        
    def do_get_curr_limit(self):
        ## set current limit for a voltage source
        return self._visainstrument.query(':SENS:CURR:PROT:LEV?').strip()
    
    def do_get_current(self):
        '''
        gets the current on the selected channel

        '''
        return self._visainstrument.query(':READ?').strip().split(',')[1]

    def _ramp_current(self, value, ramp_speed = 0.1):
        '''
        ramps the to value
        ramp_speed is rampspeed in Amps/second
        '''
        
        ## enable auto measurement
        self._visainstrument.write(':SENS:VOLT:RANG:AUTO ON')
        
        ## ramp current
        cur_val = self.get_current()
        dI = 1.*value - cur_val
        Ires = self._Ires
        n_steps = abs(int(dI/Ires))

        for k in range(n_steps):
            self._visainstrument.write(':SOUR:CURR:LEV %s A' % (1.*k)/n_steps*dI+cur_val)
            qt.msleep(Ires/ramp_speed)
            if(int(self._visainstrument.query(':SENS:VOLT:PROT:TRIP?')) == 0):
                print 'Compliance limit of %s reached, stopping ramp \n' % self._visainstrument.query(':SENS:VOLT:PROT:TRIP?')
                self._visainstrument.write(':SOUR:CURR:LEV %s A' % 0.0)
                break

        return 'A current of %s Amps has been set' \
            %(self.do_get_current())



    def do_set_voltage(self,V):
        '''
        sets the voltage on the selected channel
        mind the max and min voltage

        '''
        
        ## Set current source, and voltage sense
        self._visainstrument.query(':OUTP OFF;*OPC?')
        self._visainstrument.query(':SOUR:FUNC VOLT;*OPC?')
        self._visainstrument.query(':SENS:FUNC "CURR";*OPC?')
        self._visainstrument.query(':SOUR:VOLT:LEV %s;*OPC?' % str(V))
        self._visainstrument.query(':OUTP ON;*OPC?')
        
#        self._ramp_voltage(V)

    def do_set_volt_limit(self,Vmax):
        ## Set the maximum voltage for current source
        self._visainstrument.write('SENS:VOLT:PROT:LEV %s' % Vmax)
    
    def do_get_voltage(self):
        '''
        gets the voltage on the selected channel

        '''
        return self._visainstrument.query(':READ?').strip().split(',')[0]

    def _ramp_voltage(self, value, ramp_speed = 0.1):
        '''
        ramps the to value
        ramp_speed is rampspeed in Volts/second
        '''
        cur_val = self.get_voltage()
        dV = 1.*value - cur_val
        Vres = self._Vres
        n_steps = abs(int(dV/Vres))

        for k in range(n_steps):
            self._visainstrument.write(':SOUR:VOLT:LEV %s V' % (1.*k)/n_steps*dV+cur_val)
            qt.msleep(Vres/ramp_speed)
            if(int(self._visainstrument.query(':SENS:CURR:PROT:TRIP?')) == 0):
                print 'Compliance limit of %s reached, stopping ramp \n' % self._visainstrument.query(':SENS:CURR:PROT:TRIP?')
                self._visainstrument.write(':SOUR:VOLT:LEV %s V' % 0.0)
                break

        return 'A voltage of %s Volts has been set' \
            %(self.do_get_voltage())

    def read_data(self):
        return self._visainstrument.query(':READ?').strip().split(',')





