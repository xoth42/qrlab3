# Driver for OPTO Dac  0.1
# Stevan Nadj-Perge <s.nadj-perge@tudelft.nl>, 2008
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

from time import sleep
import types
import logging
import pyvisa
from .instrument import Instrument
from lib import visafunc


class OPTO(Instrument):

    def __init__(self, name, address, numdacs=8):
        logging.info(__name__+ ': Initializing instrument OPTO')
        Instrument.__init__(self, name, tags=['physical'])
        self._address=address
        self._numdacs=8
        self._sleeptime=0.0
        self.add_parameter('dac', type=float,
                        flags=Instrument.FLAG_SET, channels=(1, self._numdacs),
                           minval=-5000.00, maxval=5000, units='mV',
                           format='%.02f', tags=['sweep'])

        self._open_serial_connection()

    def _open_serial_connection(self):
        logging.debug(__name__+':Opening serial connection')
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

    def _send_message(self, message):
        self._vi.write_raw(message.encode('latin1'))
        sleep(self._sleeptime)

    def _dac_voltage_to_message(self, dac, voltage):
        bytevalue=int(round(voltage*1000/5000*32768+32768))
        dataH=int(bytevalue/256)
        dataL=bytevalue-dataH*256
        bytedac=128
        for _ in range(max(0, dac - 1)):
            bytedac = int(bytedac / 2)
        message=f"{7:c}{0:c}{3:c}{10:c}{bytedac:c}{dataH:c}{dataL:c}"
        return message

    def _read_buffer(self):
        navail = visafunc.get_navail(self._vi)
        response = visafunc.readn(self._vi, navail)
        sleep(self._sleeptime)
        if isinstance(response, (bytes, bytearray)):
            response = response.decode('latin1')
        return response

    def do_set_dac(self, mvoltage, channel):
        logging.debug(__name__ + 'setting the dacs')
        voltage=mvoltage/1000.0
        message=self._dac_voltage_to_message(channel, voltage)
        self._send_message(message)
        r=self._read_buffer()
        czero=f'{0:c}'
        if (r!=''):
            if (r[1]!=czero):
                logging.debug(__name__+' possible error in optodac' + r)
