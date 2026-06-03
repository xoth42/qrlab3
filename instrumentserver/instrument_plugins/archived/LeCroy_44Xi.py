# LeCroy_44Xi.py class, to perform the communication between the Wrapper and the device
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
import pyvisa
import types
import logging

class LeCroy_44Xi(Instrument):
    '''
    This is the python driver for the LeCroy Waverunner 44Xi
    Digital Oscilloscope

    Usage:
    Initialize with
    <name> = instruments.create('name', 'LeCroy_44Xi', address='<VICP address>')
    <VICP address> = VICP::<ip-address>
    '''

    def __init__(self, name, address):
        '''
        Initializes the LeCroy 44Xi.

        Input:
            name (string)    : name of the instrument
            address (string) : VICP address

        Output:
            None
        '''
        logging.debug(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])


        self._address = address
        self._visainstrument = pyvisa.ResourceManager().open_resource(self._address)
        self._values = {}

        # Add parameters
        self.add_parameter('timebase', type=float,
            flags=Instrument.FLAG_GETSET)
        self.add_parameter('vertical', type=float,
            flags=Instrument.FLAG_GETSET, channels=(1, 4),
            channel_prefix='ch%d_')
        self.add_parameter('msize', type=float,
            flags=Instrument.FLAG_GETSET)

        # Make Load/Delete Waveform functions for each channel
        for ch in range(1, 5):
            self._add_save_data_func(ch)

        self.get_all()

    # Functions
    def get_all(self):
        '''
        Get all parameter values
        '''
        self.get_timebase()
        self.get_ch1_vertical()
        self.get_ch2_vertical()
        self.get_ch3_vertical()
        self.get_ch4_vertical()
        self.get_msize()

    def set_trigger_stop(self):
        '''
        Change the aquisition state from Stopped to Single.

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Set trigger to single')
        self._visainstrument.write('TRMD SINGLE; ARM')

    def set_trigger_normal(self):
        '''
        Change the trigger mode to Normal.

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Set trigger to normal')
        self._visainstrument.write('TRMD NORMAL')

    def set_trigger_auto(self):
        '''
        Change the trigger mode to Auto.

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Set trigger to auto')
        self._visainstrument.write('TRMD AUTO')

    def auto_setup(self):
        '''
        Adjust vertical, timebase and trigger parameters automatically

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Auto setup of vertical, timebase and trigger')
        self._visainstrument.write('ASET')

    def do_set_timebase(self, value):
        '''
        Modify the timebase setting in Sec/div.

        Input:
            value (str) : Timebase in S. (NS (nanosec), US (microsec), MS (milisec),
                S (sec) or KS (kilosec))
                (Example: '50E-6', '50 MS')

        Output:
            None
        '''
        logging.info(__name__ + f' : Set timebase setting to {value}')
        self._visainstrument.write(f'TDIV {value}')

    def do_get_timebase(self):
        '''
        Get the timebase setting in Sec/div.

        Input:
            None

        Output:
            value (str) : Timebase in S
        '''
        logging.info(__name__ + ' : Get timebase setting')
        result = self._visainstrument.query('TDIV?')
        result = result.replace('TDIV ','')
        result = result.replace(' S','')
        return float(result)

    def do_set_vertical(self, value, channel):
        '''
        Set vertical sensitivity in Volts/div.

        Input:
            value (str) : Vertical base in V. (UV (microvolts), MV (milivolts),
                V (volts) or KV (kilovolts))
                (Example: '20E-3', '20 MV')
            channel (int) : channel (1,2,3,4)

        Output:
            None
        '''
        logging.info(__name__ + f' : Set vertical base setting of channel {channel} to {value}')
        self._visainstrument.write(f'C{channel}:VDIV {value}')

    def do_get_vertical(self, channel):
        '''
        Get vertical sensitivity in Volts/div.

        Input:
            channel (int) : channel (1,2,3,4)

        Output:
            value (str) : Vertical base in V.
        '''
        logging.info(__name__ + f' : Get vertical base setting of channel {channel}')
        result = self._visainstrument.query(f'C{channel}:VDIV?')
        result = result.replace(f'C{channel}:VDIV ','')
        result = result.replace(' V','')
        return float(result)

    def screen_dump(self, file, type='JPEG', background='BLACK', dir='E:\\',
    area='FULLSCREEN'):
        '''
        Initiate a screen dump

        Input:
            file(str) : destination filename, auto incremented
            type(str) : image type (PSD, BMP, BMPCOMP, JPEG (default), PNG, TIFF)
            background(str) : background color (BLACK (default), WHITE)
            dir(str) : destination directory (E:\\ is the default shared folder)
            area(str) : hardcopy area (GRIDAREAONLY, DSOWINDOW, FULLSCREEN)

        Output:
            None
        '''
        logging.info(__name__ + f' : Take a screenshot with filename {file}, type {type} and save on harddisk {dir}')
        self._visainstrument.write(f'HCSU DEV, {type}, BCKG, {background}, DEST, FILE, DIR, {dir}, FILE, {file}, AREA, {area}; SCDP')

    def _do_save_data(self, channel):
        '''
        Store a trace in ASCII format in internal memory

        Input:
            channel(int) : channel

        Output:
            None
        '''
        logging.info(__name__ + f' : Save data for channel {channel}')
        self._visainstrument.write(f'STST C{channel},HDD,AUTO,OFF,FORMAT,ASCII; STO')

    def _add_save_data_func(self, channel):
        '''
        Adds save_ch[n]_data functions, based on _do_save_data(channel).
        n = (1,2,3,4) for 4 channels.
        '''
        func = lambda: self._do_save_data(channel)
        setattr(self, f'save_ch{channel}_data', func)

    def sequence(self, segments, max_size):
        '''
        Set the sequence mode on and set number of segments, maximum memory size.
        Input:
            segments(int) : number of segments. max: 2000.
            max_size(float) : maximum memory length. Format: {10e3, 10.0e3, 11e+3, 25K, 10M (mili), 10MA (mega))

        Output:
            None
        '''
        logging.info(__name__ + f' : Set the sequence mode settings. Segments: {segments}, Maximum memory size: {max_size}')
        self._visainstrument.write(f'SEQ ON, {segments}, {max_size}')

    def do_set_msize(self, msize):
        '''
        Set the current maximum memory length used to capture waveforms.
        Input:
            msize(float) : Max. memory length size in Samples.
        Output:
            None
        '''
        logging.info(__name__ + f' : Set maximum memory length to {msize}')
        self._visainstrument.write(f'MSIZ {msize}')

    def do_get_msize(self):
        '''
        Get the current maximum memory length used to capture waveforms.
        Input:
            None
        Output:
            result(float) : maximum memory size in Samples
        '''
        logging.info(__name__ + ' : Get maximum memory length')
        result = self._visainstrument.query('MSIZ?')
        result = result.replace('MSIZ ', '')
        result = result.replace(' SAMPLE', '')
        return float(result)
