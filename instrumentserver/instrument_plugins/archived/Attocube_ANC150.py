# Attocube_ANC150, attocube piezo step controller ANC150 driver
# Reinier Heeres <reinier@heeres.eu>, 2008
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
import re
import time
import copy

class Attocube_ANC150(Instrument):

    _RE_MODE = re.compile('mode = (\w+)')
    _RE_FREQ = re.compile('frequency = (\d+) Hz')
    _RE_VOLT = re.compile('voltage = (\d+) V')
    _RE_CAP = re.compile('capacitance = (\d+) C')
    _RE_SN = re.compile('serial number (\d+)')
    _RE_VER = re.compile('version (.*)')

    _ERRMSG_AXIS = "Axis not in computer control mode"

    def __init__(self, name, address, reset=False, **kwargs):
        Instrument.__init__(self, name, address=address, reset=False, **kwargs)

        self._address = address
        self._visa = pyvisa.ResourceManager().open_resource(self._address)
        self._visa.baud_rate = 38400
        self._visa.data_bits = 8
        self._visa.stop_bits = pyvisa.constants.StopBits.one
        self._visa.parity = pyvisa.constants.Parity.none
        self._visa.read_termination = '\r\n'
        self._visa.write_termination = '\r\n'
        self._visa.timeout = 2000
        self._clear_buffer()
        self._last_error = ''
        self._last_ccon_warning = [0, 0, 0]

        self.add_parameter('version',
            flags=Instrument.FLAG_GET,
            type=bytes)

        self.add_parameter('mode',
            flags=Instrument.FLAG_GETSET,
            channels=(1, 3),
            type=bytes,
            format_map={
                'e': 'ext',
                's': 'stp',
                'g': 'gnd',
                'c': 'cap',
            },
            doc="mode is one of 'ext', 'stp', 'gnd' or 'cap', or first letter")

        self.add_parameter('frequency',
            flags=Instrument.FLAG_GETSET,
            channels=(1, 3),
            type=int,
            minval=0, maxval=8000)

        self.add_parameter('voltage',
            flags=Instrument.FLAG_GETSET,
            channels=(1, 3),
            type=int,
            minval=0, maxval=70)

        self.add_parameter('capacitance',
            flags=Instrument.FLAG_GET,
            channels=(1, 3),
            type=int)

        self._speed = [0, 0, 0]
        self.add_parameter('speed',
            type=tuple,
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
            doc="""
            Set speed for continuous motion mode.
            """)

        self.add_function('step', parameters=[{
                'name': 'channel',
                'type': int,
            }, {
                'name': 'steps',
                'type': int,
            }])

        self.add_function('start')
        self.add_function('stop')

        if reset:
            self.reset()
        else:
            self.get_all()

    def _clear_buffer(self):
        self._visa.clear()
        time.sleep(0.02)
        self._visa.write('')

    def get_last_error(self):
        '''Return last error message.'''
        return self._last_error

    def _ask(self, query):
        self._visa.write(query)
        line, lastline = '', ''
        for _ in range(100):
            if line.startswith('OK') or line.startswith('ERROR'):
                break
            lastline = line
            line = self._visa.read()
        else:
            raise IOError('ANC150 reply exceeded 100 lines')
        if line.startswith('ERROR'):
            self._last_error = lastline
            return None
        return lastline

    def _short_cmd(self, query):
        self._visa.write(query)
        line = self._visa.read()
        if line.find('+') != -1:
            return True
        else:
            return False

    def _parse(self, reply, regexp):
        if reply is None:
            return None

        m = regexp.search(reply)
        if m is None:
            return None
        else:
            return m.group(1)

    def reset(self):
        '''Reset instrument.'''
        self._visa.write('resetp')

    def get_all(self):
        '''Get all parameters.'''
        for ch in range(1, 4):
            self.get(f'mode{int(ch)}')
            self.get(f'frequency{int(ch)}')
            self.get(f'voltage{int(ch)}')

    def do_get_version(self):
        reply = self._ask('ver')
        ver = self._parse(reply, self._RE_VER)
        return ver

    def do_get_mode(self, channel):
        reply = self._ask(f'getm {int(channel)}')
        return self._parse(reply, self._RE_MODE)

    def do_set_mode(self, mode, channel):
        ret = self._short_cmd(f'$M{int(channel)}{mode.upper()}')
        if ret:
            return True
        else:
            # Warn about axis not being in computer control once per minute
            ret = self.get(f'mode{int(channel)}')
            if ret is None and self.get_last_error() == self._ERRMSG_AXIS and \
                    (time.time() - self._last_ccon_warning[channel - 1]) > 60:
                self._last_ccon_warning[channel - 1] = time.time()
                logging.warning(f'Axis {int(channel)} not in computer control mode', )
            return ret

    def do_get_frequency(self, channel):
        reply = self._ask(f'getf {int(channel)}')
        return self._parse(reply, self._RE_FREQ)

    def do_set_frequency(self, freq, channel):
        reply = self._ask(f'setf {int(channel)} {int(freq)}')
        return (reply is not None)

    def do_get_voltage(self, channel):
        reply = self._ask(f'getv {int(channel)}')
        return self._parse(reply, self._RE_VOLT)

    def do_set_voltage(self, volt, channel):
        reply = self._ask(f'setv {int(channel)} {int(volt)}')
        return (reply is not None)

    def do_get_capacitance(self, channel):
        reply = self._ask(f'getc {int(channel)}')
        return self._parse(reply, self._RE_CAP)

    def step(self, channel, steps, wait=True, cont=False):
        '''
        Step channel <channel> (1, 2 or 3) by <steps> steps.

        If wait=True (default), the function will sleep until the motion
        is finished.

        If cont=True (not default), the function will put the positioner
        in continuous motion. Use stop() to stop this motion.
        '''

        if type(steps) is not int:
            logging.warning('Integer number of steps required')
            return False
        if steps == 0:
            return True

        if channel < 1 or channel > 3:
            logging.warning('Channel has to be between 1 and 3')
            return False

        if steps > 0:
            dir = 'u'
        else:
            dir = 'd'
            steps = -steps
        if cont:
            steps = 'c'
            delay = 0
        else:
            frequency = self.get(f'frequency{int(channel)}', query=False)
            if frequency in (None, 0):
                frequency = self.get(f'frequency{int(channel)}')
            delay = 1.1 * steps / frequency

        if steps == 1 and not cont:
            func = lambda: self._short_cmd(f'$S{int(channel)}{dir.upper()}')
        else:
            func = lambda: self._ask(f'step{dir} {int(channel)} {steps}')

        reply = func()
        if not reply:
            logging.info(f'Axis {int(channel)} problem, trying to set mode', )
            self.set(f'mode{int(channel)}', 's')
            reply = func()

        if wait:
            time.sleep(delay)

        return (reply is not None)

    def do_set_speed(self, val):
        for i in range(len(self._speed)):
            if self._speed[i] != val[i]:
                self.set(f'frequency{int(i + 1)}', int(abs(val[i])))
        self._speed = copy.copy(val)

    def start(self):
        '''
        Start continuous motion using the speed property for each channel.
        '''

        for i in range(len(self._speed)):
            mode = self.get(f'mode{int(i + 1)}', query=False)

            self.set(f'mode{int(i + 1)}', 'stp')
            if self._speed[i] > 0:
                reply = self._ask(f'stepu {int(i + 1)} c')
            elif self._speed[i] < 0:
                reply = self._ask(f'stepd {int(i + 1)} c')
            else:
                reply = True

            if not reply:
                logging.info(f'Problem setting axis {int(i)}' + 1, )

    def stop(self, channel=None):
        '''
        Stop continuous motion.
        If channel=None (default) all channels will be halted.
        '''
        if channel is None:
            for i in range(len(self._speed)):
                self._ask(f'stop {int(i + 1)}')
        else:
            self._ask(f'stop {int(channel)}')
