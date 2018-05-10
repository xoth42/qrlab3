from instrument import Instrument
import types
import visa
from lib import visafunc
import numpy as np
import objectsharer as objsh
import logging
logging.getLogger().setLevel(logging.DEBUG)

DEFAULT_TIMEOUT = 2000

class VisaInstrument(Instrument):

    def __init__(self, name, address=None, term_chars=None, **kwargs):
        super(VisaInstrument, self).__init__(name)

        self._ins = None
        self._address = None
        self._interrupted = False
        self._term_chars = term_chars

        self.add_parameter('address', type=types.StringType)
        self.add_parameter('timeout', type=types.IntType, value=DEFAULT_TIMEOUT,
                           units='ms',
                           help='Instrument read timeout')

        self.set_timeout(DEFAULT_TIMEOUT)
        if address:
            self.set_address(address)

        self.clear()
        self.set(kwargs)

    def interrupt(self):
        self._interrupted = True

    def do_set_address(self, val):
        if self._address == val and val is not None:
            return
        self._address = val
        self.close()
        self.open()

    def do_get_address(self):
        return self._address

    def do_set_timeout(self, val):
        N = 1
        while val > 1000:
            val /= 2
            N *= 2
        self._timeout = val
        self._Ntimeout = N
        if self._ins:
            self._ins.timeout = np.ceil(val / 1000.0)

    def do_get_timeout(self):
        return self._timeout * self._Ntimeout

    def set_term_chars(self, val):
        self._term_chars = term_chars
        if self._ins:
            self._ins.term_chars = term_chars

    def open(self):
        logging.debug('Opening visa instrument at address %s, term_chars=%r', self._address, self._term_chars)
        try:
            self._ins = visa.instrument(self._address, term_chars=self._term_chars, timeout=self._timeout)
        except Exception, e:
            msg = 'Unable to open instrument %s' % (self._address,)
            logging.error(msg)

    def close(self):
        if self._ins:
            self._ins.close()
        self._ins = None

    def reopen(self):
        self.close()
        self.open()

    def _check_ins(self):
        if self._ins is None:
            raise Exception('instrument not opened')

    def read(self):
        self._check_ins()
        for i in range(self._Ntimeout):
            try:
                ret = self._ins.read()
                return ret
            except:
                pass
            if objsh.helper.backend:
                objsh.helper.backend.main_loop(0)
            if self._interrupted:
                self._interrupted = False
                raise Exception('Interrupted')

    def read_raw(self):
        self._check_ins()
        return self._ins.read_raw()

    def write(self, cmd):
        self._check_ins()
        return self._ins.write(cmd)

    def ask(self, cmd, timeout=None):
        self.write(cmd)
        return self.read()

    def clear(self):
        self._check_ins()
        self._ins.clear()
        visafunc.read_all(self._ins)

    def get_visa_param(self, channel):
        p = self.get_parameter_options(channel)
        return self.ask(p['getfmt'])

    def set_visa_param(self, val, channel):
        p = self.get_parameter_options(channel)
        return self.write(p['setfmt']%val)

    def add_visa_parameter(self, name, getfmt, setfmt, **kwargs):
        kwargs['getfmt'] = getfmt
        kwargs['setfmt'] = setfmt
        self.add_parameter(name,
            get_func=self.get_visa_param, set_func=self.set_visa_param,
            channel=name, **kwargs)

    # Close Visa handle if removed
    def remove(self):
        self.close()
