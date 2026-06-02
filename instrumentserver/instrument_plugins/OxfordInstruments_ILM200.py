# OxfordInstruments_ILM200.py class, to perform the communication between the Wrapper and the device
# Guenevere Prawiroatmodjo <guen@vvtp.tudelft.nl>, 2009
# Pieter de Groot <pieterdegroot@gmail.com>, 2009
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

from .instrument import Instrument
from time import time, sleep
import pyvisa
import types
import logging

class OxfordInstruments_ILM200(Instrument):
    '''
    This is the python driver for the Oxford Instruments ILM 200 Helium Level Meter.

    Usage:
    Initialize with
    <name> = instruments.create('name', 'OxfordInstruments_ILM200', address='<Instrument address>')
    <Instrument address> = ASRL1::INSTR

    Note: Since the ISOBUS allows for several instruments to be managed in parallel, the command
    which is sent to the device starts with '@n', where n is the ISOBUS instrument number.

    '''
#TODO: auto update script
#TODO: get doesn't always update the wrapper! (e.g. when input is an int and output is a string)

    def __init__(self, name, address, number=1):
        '''
        Initializes the Oxford Instruments ILM 200 Helium Level Meter.

        Input:
            name (string)    : name of the instrument
            address (string) : instrument address
            number (int)     : ISOBUS instrument number

        Output:
            None
        '''
        logging.debug(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])


        self._address = address
        self._number = number
        self._visainstrument = pyvisa.ResourceManager().open_resource(self._address)
        self._values = {}
        self._visainstrument.stop_bits = pyvisa.constants.StopBits.two

        #Add parameters
        self.add_parameter('level', type=float,
            flags=Instrument.FLAG_GET)
        self.add_parameter('status', type=bytes,
            flags=Instrument.FLAG_GET)

        # Add functions
        self.add_function('get_all')
        self.get_all()

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
        self.get_level()
        self.get_status()

    # Functions
    def _execute(self, message):
        '''
        Write a command to the device

        Input:
            message (str) : write command for the device

        Output:
            None
        '''
        logging.info(__name__ + f' : Send the following command to the device: {message}')
        self._visainstrument.write(f'@{self._number}{message}')
        sleep(20e-3) # wait for the device to be able to respond
        result = self._visainstrument.read()
        if result.find('?') >= 0:
            print(f"Error: Command {message} not recognized")
        else:
            return result

    def identify(self):
        '''
        Identify the device

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Identify the device')
        return self._execute('V')

    def remote(self):
        '''
        Set control to remote & locked

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Set control to remote & locked')
        self.set_remote_status(1)

    def local(self):
        '''
        Set control to local & locked

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Set control to local & locked')
        self.set_remote_status(0)

    def set_remote_status(self, mode):
        '''
        Set remote control status.

        Input:
            mode(int) :
            0 : "Local and locked",
            1 : "Remote and locked",
            2 : "Local and unlocked",
            3 : "Remote and unlocked",

        Output:
            None
        '''
        status = {
        0 : "Local and locked",
        1 : "Remote and locked",
        2 : "Local and unlocked",
        3 : "Remote and unlocked",
        }
        logging.info(__name__ + f" : Setting remote control status to {status.get(mode, 'Unknown')}")
        self._execute(f'C{mode}')

    def do_get_level(self):
        '''
        Get Helium level of channel 1.
        Input:
            None

        Output:
            result (float) : Helium level
        '''
        logging.info(__name__ + ' : Read level of channel 1')
        result = self._execute('R1')
        return float(result.replace('R',''))

    def do_get_status(self):
        '''
        Get status of the device.
        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Get status of the device.')
        result = self._execute('X')
        status = {
        0 : "Channel not in use",
        1 : "Channel used for Nitrogen level",
        2 : "Channel used for Helium Level (Normal pulsed operation)",
        3 : "Channel used for Helium Level (Continuous measurement)",
        9 : "Error on channel (Usually means probe unplugged)"
        }
        return status.get(int(result[1]), "Unknown")
