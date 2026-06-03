import time
from instrumentserver.instrument import Instrument
import objectsharer as objsh
import logging
logging.getLogger().setLevel(logging.INFO)

import pyvisa
from pyvisa.errors import VisaIOError
from pyvisa.constants import StatusCode

DEFAULT_TIMEOUT = 2000


class VisaInstrument(Instrument):

    def __init__(self, name, address=None, term_chars=None, **kwargs):
        super(VisaInstrument, self).__init__(name)

        self._ins = None
        self._address = None
        self._interrupted = False
        self._term_chars = term_chars
        self._timeout = DEFAULT_TIMEOUT

        self.add_parameter('address', type=bytes)
        self.add_parameter('timeout', type=int, value=DEFAULT_TIMEOUT,
                           units='ms',
                           help='Instrument read timeout')

        self._resource_manager = pyvisa.ResourceManager()

        if address:
            self.set_address(address)

        if self._ins is not None:
            self.clear()
        self.set(kwargs)

    def interrupt(self):
        self._interrupted = True

    def do_set_address(self, val):
        if self._address == val and val is not None:
            return
        self._address = val
        self.reopen()

    def do_get_address(self):
        return self._address

    def do_set_timeout(self, val):
        self._timeout = val
        if self._ins:
            self._ins.timeout = val


    def do_get_timeout(self):
        return self._timeout

    def set_term_chars(self, term_chars):
        self._term_chars = term_chars
        if self._ins:
            self._ins.read_termination = term_chars

    def open(self):
        logging.debug(f'Opening visa instrument at address {self._address}, term_chars={self._term_chars!r}', )
        try:
            self._ins = self._resource_manager.open_resource(self._address)
            if self._term_chars is not None:
                self._ins.read_termination = self._term_chars
                self._ins.write_termination = self._term_chars
            self._ins.timeout = self._timeout

        except Exception:
            msg = f'Unable to open instrument {self._address}'
            logging.error(msg)
            raise

    def _check_ins(self):
        if self._ins is None:
            raise Exception("instrument not opened")

    def close(self):
        if self._ins:
            self._ins.close()
        self._ins = None

    def reopen(self):
        self.close()
        self.open()

    def read(self):
        self._check_ins()
        deadline = time.monotonic() + (self._timeout / 1000.0)
        old_timeout = self._ins.timeout
        self._ins.timeout = 0
        try:
            for _ in range(max(1, self._timeout * 10)):
                if time.monotonic() >= deadline:
                    raise Exception(f"Instrument read timed out (timeout={self._timeout})")
                try:
                    ret = self._ins.read()
                    break
                except VisaIOError as e:
                    if not self._is_timeout_error(e):
                        raise e
                objsh.backend.main_loop(0)
            else:
                raise Exception(f"Instrument read timed out (timeout={self._timeout})")
            if self._interrupted:
                self._interrupted = False
                raise Exception("Interrupted")
        finally:
            self._ins.timeout = old_timeout

        return ret

    def _is_timeout_error(self, exc):
        if getattr(exc, 'error_code', None) == StatusCode.error_timeout:
            return True
        return getattr(exc, 'error_code', None) in ('VI_ERROR_TMO', -1073807339)

    def read_raw(self):
        self._check_ins()
        return self._ins.read_raw()

    def write(self, cmd):
        self._check_ins()
        return self._ins.write(cmd)

    def write_raw(self, cmd):
        self._ins.write_raw(cmd)

    def ask(self, cmd, timeout=None):
        self._check_ins()
        if timeout is None:
            return self._ins.query(cmd).strip()

        old_timeout = self._ins.timeout
        self._ins.timeout = timeout
        try:
            return self._ins.query(cmd).strip()
        finally:
            self._ins.timeout = old_timeout

    def clear(self):
        self._check_ins()
        self._ins.clear()

    def get_visa_param(self, channel):
        p = self.get_parameter_options(channel)
        return self.ask(p['getfmt'])

    def set_visa_param(self, val, channel):
        p = self.get_parameter_options(channel)
        self.write(p['setfmt'] % val)
        for name in p.get('updates', []):
            print(f'updating {name}')
            self.get(name)

    def add_visa_parameter(self, name, getfmt, setfmt, **kwargs):
        kwargs['getfmt'] = getfmt
        kwargs['setfmt'] = setfmt
        self.add_parameter(name,
            get_func=self.get_visa_param, set_func=self.set_visa_param,
            channel=name, **kwargs)

    # Close Visa handle if removed
    def remove(self):
        self.close()


class SCPI_Instrument(VisaInstrument):
    def add_scpi_parameter(self, name, scpi_cmd, scpi_fmt='%s', **kwargs):
        getfmt = scpi_cmd + "?"
        setfmt = scpi_cmd + " " + scpi_fmt
        self.add_visa_parameter(name, getfmt, setfmt, **kwargs)
