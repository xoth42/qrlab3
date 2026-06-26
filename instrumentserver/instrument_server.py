import logging
import os
import sys

# Repo root, so `lib.server_support` is importable regardless of cwd (this
# subprocess is normally launched with cwd=instrumentserver/, for the
# relative 'instrument_plugins' sys.path entry added below).
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.server_support.log_rotate import (INSTRUMENT_SERVER_LOG_ENV,
                                           attach_log_from_env)
from lib.server_support.uselogs import configure_logging

attach_log_from_env(INSTRUMENT_SERVER_LOG_ENV)
configure_logging()

import sys
import time

import pythonprocess

import objectsharer as objsh


def close():
    logging.info('Closing instrument instance')
    sys.exit()

if __name__ == '__main__':
    logging.info('Starting instrument server...')

    parser = pythonprocess.ArgParser(description='Instrument server')
    parser.add_option('--isrv', type=str, default='tcp://127.0.0.1:55555',
        help='Instruments server location')
    parser.add_option('--insname', type=str, default=None,
        help='Instrument name')
    parser.add_option('--instype', type=str, default=None,
        help='Instrument type')
    parser.add_option('--kwargs', type=str, default=None,
        help='Base64 encoded pickled keyword arguments')
#    parser.add_option('--address', type=str, default=None,
#        help='Address')
#    parser.add_option('--reset', type=str, default=None,
#        help='Reset?')

    args, kwargs = parser.parse_args()

    # This of course looks really confusing, but it is what we want...
    if kwargs['kwargs'] is not None:
        kwargs.update(kwargs['kwargs'])
    del kwargs['kwargs']

    # Pop all used arguments so that rest can be passed to the instrument
    insname = kwargs.pop('insname', None)
    instype = kwargs.pop('instype', None)
    isrv = kwargs.pop('isrv')

    if insname is None or instype is None:
        raise ValueError('Instrument name and type required')
    logging.info('  Creating instrument %s of type %s' % (insname, instype))

    sys.path.append('instrument_plugins')
    sys.path.append('user_instruments')

    start = time.time()
    insmod = __import__(instype)
    insclass = getattr(insmod, instype, None)
    
    if insclass is None:
        raise ValueError('Instrument module does not contain instrument class')
    end = time.time()
    logging.debug('Loading instrument module %.03f sec', end - start)

    logging.debug('Starting sharing server and connecting to %s' % isrv)
    if hasattr(objsh, 'ZMQBackend'):
        backend = objsh.ZMQBackend()
    else:
        backend = objsh.backend
    backend.start_server(addr='127.0.0.1')
    backend.connect_to(isrv)

    logging.debug('Creating instrument, name %s, kwargs %s' % (insname, kwargs))
    start = time.time()
    ins = insclass(insname, **kwargs)
    ins.set_remove_cb(close)
    end = time.time()
    logging.debug('Creating instrument took %.03f sec', end - start)

    objsh.register(ins, name=insname)

    time.sleep(1)

    instruments = objsh.helper.find_object('instruments')
    ins.set_instruments(instruments)
    instruments.remove(insname)
    instruments.register_instrument(ins)
    backend.main_loop()
    ins.close()
    instruments.remove(insname)
    instruments.register_instrument(ins)
    backend.main_loop()
    ins.close()
