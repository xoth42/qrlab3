from .instrument import Instrument
import time
import pyvisa
import types
import math

class BNC_RFsource(Instrument):

    def __init__(self, name, address, **kwargs):
        super(BNC_RFsource, self).__init__(name, **kwargs)

        self._address = address
        self.open()

        self.add_parameter('rf_on', type=bool,
            flags=Instrument.FLAG_GETSET)
        self.add_parameter('lock_src', type=bytes,
            flags=Instrument.FLAG_GETSET,
            option_list=('INT', 'EXT'))
        self.add_parameter('extref_freq', type=float,
            flags=Instrument.FLAG_GETSET,
            minval=1e6, maxval=100e6)
        self.add_parameter('locked', type=bool,
            flags=Instrument.FLAG_GET)
        self.add_parameter('power', type=float,
            flags=Instrument.FLAG_GETSET, units='dBm', minval=-135, maxval=16)
        self.add_parameter('phase', type=float,
            flags=Instrument.FLAG_GETSET, units='rad', minval=-math.pi, maxval=math.pi)
        self.add_parameter('frequency', type=float,
            flags=Instrument.FLAG_GETSET, units='Hz',
            minval=1e5, maxval=20e9, display_scale=6)

        self.add_function('lock')

        if kwargs.pop('reset', False):
            self.reset()
        else:
            self.get_all()
        self.set(kwargs)

    def open(self):
        self._ins = pyvisa.ResourceManager().open_resource(self._address)
        self._ins.read_termination = '\n'
        self._ins.write_termination = '\n'
        self._ins.timeout = 10000

    def ask(self, q):
        try:
            return self._ins.query(q)
        except:
            pass
        self.open()
        return self._ins.query(q)

    def write(self, q):
        try:
            return self._ins.write(q)
        except:
            pass
        self.open()
        return self._ins.write(q)

    def read(self):
        try:
            return self._ins.read()
        except:
            pass
        self.open()
        return self._ins.read()

    def do_get_rf_on(self):
        val = self.ask('OUTP?\n')
        return bool(int(val))

    def do_set_rf_on(self, on):
        self.write(f'OUTP {int(bool(on))}\n')

    def do_get_frequency(self):
        val = self.ask(':FREQ?\n')
        return float(val)

    def do_set_frequency(self, freq):
        self.write(f':FREQ {freq:.6f}\n')

    def do_get_phase(self):
        val = self.ask(':PHASE?\n')
        return float(val)

    def do_set_phase(self, phase):
        self.write(f':PHASE {phase:.3f}\n')

    def do_get_power(self):
        return 15

    def do_get_locked(self):
        val = self.ask(':ROSC:LOCK?')
        return bool(int(val))

    def do_get_extref_freq(self):
        '''Return external reference frequency.'''
        val = self.ask(':ROSC:EXT:FREQ?')
        return float(val)

    def do_set_extref_freq(self, val=10e6):
        '''Set external reference frequency.'''
        self.write(f':ROSC:EXT:FREQ {val:.3f}')

    def do_get_lock_src(self):
        val = self.ask(':ROSC:SOUR?')
        return val

    def do_set_lock_src(self, val):
        self.write(f':ROSC:SOUR {val}')

    def lock(self, freq=10e6):
        self.set_extref_freq(freq)
        self.set_lock_src('EXT')

if __name__ == '__main__':
    Instrument.test(BNC_RFsource)
