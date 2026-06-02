# Coincidence.py
# Reinier Heeres <reinier@heeres.eu>, 2011
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
import types
import time
import logging
import pyvisa
from lib import visafunc

class Coincidence(Instrument):
    '''
    '''

    def __init__(self, name, address, reset=False):
        Instrument.__init__(self, name, tags=['physical'])
        self._address = address

        # Add parameters
        self.add_parameter('measurement_time',
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
            type=int, minval=1, maxval=65535, units='dsec')

        self._open_serial_connection()

        self.add_function('get_all')

        if reset:
            self.reset()
        else:
            self.get_all()

    def __del__(self):
        self._close_serial_connection()

    def _open_serial_connection(self):
        self._vi = pyvisa.ResourceManager().open_resource(self._address)
        self._vi.baud_rate = 115200
        self._vi.data_bits = 8
        self._vi.stop_bits = pyvisa.constants.StopBits.one
        self._vi.parity = pyvisa.constants.Parity.odd
        self._vi.read_termination = None
        self._vi.write_termination = None
        self._vi.send_end = False

    def _close_serial_connection(self):
        self._vi.close()

    def reset(self):
        self.set_measurement_time(0)
        time.sleep(0.1)
        self.set_measurement_time(1)
        time.sleep(0.1)

    def _short_to_bytes(self, bytevalue):
        dataH = int(bytevalue/256)
        dataL = bytevalue - dataH*256
        return (dataH, dataL)

    def do_set_measurement_time(self, dt):
        (DataH, DataL) = self._short_to_bytes(dt)
        message = f"{DataH:c}{DataL:c}"
        self._vi.write_raw(message.encode('latin1'))

    def start(self):
        mt = self.get_measurement_time()
        self.do_set_measurement_time(0)
        time.sleep(0.1)
        self.do_set_measurement_time(mt)

    def read(self):
        data = visafunc.read_all(self._vi)
        # PyVISA may return either bytes or legacy text depending on version.
        if isinstance(data, str):
            data = data.encode('latin1')
        ret = ''
        for c in data:
            ret += f'{c:02x},'
        print(f'Read {len(data)} bytes')
        print(f'Data: {ret}')
