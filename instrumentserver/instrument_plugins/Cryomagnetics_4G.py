# Cryomagnetics_CS4, Cryomagnetics CS4 magnet power supply driver
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
import math
import time
import re

class Cryomagnetics_4G(Instrument):

    UNITS = ['A', 'G']
    MARGIN = 0.001  # 1 Gauss
    RE_ANS = re.compile(r'(-?\d*\.?\d*)([a-zA-Z]+)')

    def __init__(self, name, address, reset=False, axes=('Z')):
        Instrument.__init__(self, name)

        self._axes = {}
        for i in range(len(axes)):
            self._axes[i+1] = axes[i]
        self._address = address
        self._visa = pyvisa.ResourceManager().open_resource(self._address)

        self.add_parameter('identification',
            flags=Instrument.FLAG_GET)

        self.add_parameter('units',
            flags=Instrument.FLAG_GETSET,
            channels=axes,
            option_list=self.UNITS,
            type=bytes)

        self.add_parameter('rate0',
            flags=Instrument.FLAG_GETSET,
            type=float,
            channels=axes,
            minval=0,
            units='A/s')

        self.add_parameter('rate1',
            flags=Instrument.FLAG_GETSET,
            type=float,
            channels=axes,
            minval=0,
            units='A/s')

        self.add_parameter('heater',
            flags=Instrument.FLAG_GETSET,
            channels=axes,
            type=bool,
            doc='''Persistent switch heater on?''')

        self.add_parameter('magnetout',
            flags=Instrument.FLAG_GET | Instrument.FLAG_SET,
            channels=axes,
            type=float,
            units='kG', format='%.05f',
            doc='''Magnet current (or field in kG)''')

        self.add_parameter('supplyout',
            flags=Instrument.FLAG_GET,
            channels=axes,
            type=float,
            units='kG', format='%.05f',
            doc='''Power supply current (or field in kG)''')

        self.add_parameter('sweep',
            flags=Instrument.FLAG_GETSET,
            channels=axes,
            option_list=['UP', 'UP FAST', 'DOWN', 'DOWN FAST', 'PAUSE', 'ZERO'],
            type=bytes)

        self.add_parameter('lowlim',
            flags=Instrument.FLAG_GETSET,
            channels=axes,
            type=float,
            minval=-90.0, maxval=90.0,
            units='kG', format='%.05f')

        self.add_parameter('uplim',
            flags=Instrument.FLAG_GETSET,
            channels=axes,
            type=float,
            minval=-90.0, maxval=90.0,
            units='kG', format='%.05f')

        self.add_parameter('field',
            flags=Instrument.FLAG_GETSET,
            channels=axes,
            type=float,
            minval=-90, maxval=90.0,
            units='kG', format='%.02f',
            tags=['sweep'],
            doc='''Field in Gauss (or Amperes)''')

        self.add_function('local')
        self.add_function('remote')
        self.add_function('sweep_up')
        self.add_function('sweep_down')
        self.add_function('pause')
        self.add_function('zero')

        if reset:
            self.reset()
        else:
            self.get_all()

    def reset(self):
        self._visa.write('*RST')

    def get_all(self):
        self.get_identification()
        for ax in list(self._axes.values()):
            self.get(f'units{ax}')
            self.get(f'rate0{ax}')
            self.get(f'rate1{ax}')
            self.get(f'heater{ax}')
            self.get(f'magnetout{ax}')
            self.get(f'supplyout{ax}')
            self.get(f'lowlim{ax}')
            self.get(f'uplim{ax}')
            self.get(f'field{ax}')
            self.get(f'sweep{ax}')

    def do_get_identification(self):
        return self._visa.query('*IDN?')

    def _update_units(self, unit, channel):
        if unit == 'G':
            unit = 'kG'
        self.set_parameter_options(f'magnetout{channel}', units=unit)
        self.set_parameter_options(f'supplyout{channel}', units=unit)
        self.set_parameter_options(f'lowlim{channel}', units=unit)
        self.set_parameter_options(f'uplim{channel}', units=unit)

    def do_get_nchannels(self):
        ans = self._visa.query('CHAN?')
        if ans not in ('1', '2'):
            return 2
        else:
            return 1

    def _select_channel(self, channel):
        for i, v in self._axes.items():
            if v == channel:
                self._visa.write(f'CHAN {int(i)}')
                return True
        raise ValueError(f'Unknown axis {channel}')

    def do_get_units(self, channel):
        self._select_channel(channel)
        ans = self._visa.query('UNITS?')
        self._update_units(ans, channel)
        return ans

    def do_set_units(self, unit, channel):
        if unit not in self.UNITS:
            logging.error(f'Trying to set invalid unit: {unit}', )
            return False
        self._select_channel(channel)
        self._visa.write(f'UNITS {unit}')
        self._update_units(unit, channel)

    def _check_ans_unit(self, ans, channel):
        m = self.RE_ANS.match(ans)
        if not m:
            logging.warning(f'Unable to parse answer: {ans}', )
            return False

        val, unit = m.groups((0,1))
        try:
            val = float(val)
        except:
            val = None

        set_unit = self.get(f'units{channel}', query=False)
        if set_unit == 'G':
            set_unit = 'kG'
        if unit != set_unit:
            logging.warning(f'Returned units ({unit}) differ from set units ({set_unit})!',
                )
            return None

        return val

    def do_get_rate0(self, channel):
        self._select_channel(channel)
        ans = self._visa.query('RATE? 0')
        return float(ans)

    def do_get_rate1(self, channel):
        self._select_channel(channel)
        ans = self._visa.query('RATE? 1')
        return float(ans)

    def do_set_rate0(self, rate, channel):
        self._select_channel(channel)
        self._visa.write(f'RATE 0 {rate:.3f}\n')

    def do_set_rate1(self, rate, channel):
        self._select_channel(channel)
        self._visa.write(f'RATE 1 {rate:.3f}\n')

    def do_get_heater(self, channel):
        self._select_channel(channel)
        ans = self._visa.query('PSHTR?')
        if len(ans) > 0 and ans[0] == '1':
            return True
        else:
            return False

    def do_set_heater(self, on, channel):
        if on:
            text = 'ON'
        else:
            text = 'OFF'

        self._select_channel(channel)
        self._visa.write(f'PSHTR {text}')

    def local(self):
        self._visa.write('LOCAL')

    def remote(self):
        self._visa.write('REMOTE')

    def do_get_magnetout(self, channel):
        self._select_channel(channel)
        ans = self._visa.query('IMAG?')
        return self._check_ans_unit(ans, channel)

    def do_set_magnetout(self, val, channel):
        self._select_channel(channel)
        ans = self._visa.write(f'IMAG {val:f}\n')
        return True

    def do_get_supplyout(self, channel):
        self._select_channel(channel)
        ans = self._visa.query('IOUT?')
        return self._check_ans_unit(ans, channel)

    def do_get_sweep(self, channel):
        self._select_channel(channel)
        ans = self._visa.query('SWEEP?')
        return ans

    def do_set_sweep(self, val, channel):
        self._select_channel(channel)
        val = val.upper()
        if val not in ['UP', 'UP FAST', 'DOWN', 'DOWN FAST', 'PAUSE', 'ZERO']:
            logging.warning('Invalid sweep mode selected')
            return False
        self._visa.write(f'SWEEP {val}')

    def sweep_up(self, channel, fast=False):
        cmd = 'UP'
        if fast:
            cmd += ' FAST'
        return self.set(f'sweep{channel}', cmd)

    def sweep_down(self, channel, fast=False):
        cmd = 'DOWN'
        if fast:
            cmd += ' FAST'
        return self.set(f'sweep{channel}', cmd)

    def do_get_lowlim(self, channel):
        self._select_channel(channel)
        ans = self._visa.query('LLIM?')
        return self._check_ans_unit(ans, channel)

    def do_set_lowlim(self, val, channel):
        self._select_channel(channel)
        self._visa.write(f'LLIM {val:f}\n')

    def do_get_uplim(self, channel):
        self._select_channel(channel)
        ans = self._visa.query('ULIM?')
        return self._check_ans_unit(ans, channel)

    def do_set_uplim(self, val, channel):
        self._select_channel(channel)
        self._visa.write(f'ULIM {val:f}\n')

    def do_set_field(self, val, channel, wait=False):
        self._select_channel(channel)
        units = self.get(f'units{channel}', query=False)
        if units != 'G':
            logging.warning('Unable to set field when units not in Gauss!')
            return False

        if not self.get(f'heater{channel}', query=False):
            logging.warning('Unable to sweep field when heater off')
            return False

        cur_magnet = self.get(f'magnetout{channel}')
        cur_supply = self.get(f'supplyout{channel}')
        if math.fabs(cur_magnet - cur_supply) > self.MARGIN:
            logging.warning(f'Unable to set field when magnet ({cur_magnet:f}) and supply ({cur_supply:f}) not equal!', )
            return False

        if val > cur_magnet:
            self.set(f'uplim{channel}', val)
            self.sweep_up(channel)
        else:
            self.set(f'lowlim{channel}', val)
            self.sweep_down(channel)

        if wait:
            for _ in range(72_000):
                if math.fabs(val - self.get(f'magnetout{channel}')) <= self.MARGIN:
                    break
                time.sleep(0.050)
            else:
                raise IOError('Timed out waiting one hour for magnet sweep')

        return True

    def do_get_field(self, channel):
        self._select_channel(channel)
        unit = self.get(f'units{channel}', query=False)
        if unit != 'G':
            logging.warning('Unable to determine field if units are not Gauss')
            return None

        magnet_field = self.get(f'magnetout{channel}')
        return magnet_field

    def pause(self):
        for ax in list(self._axes.values()):
            self.set(f'sweep{ax}', 'PAUSE')

    def zero(self):
        for ax in list(self._axes.values()):
            self.set(f'sweep{ax}', 'ZERO')
