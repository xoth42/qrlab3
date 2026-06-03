import sys
import logging
logging.getLogger().setLevel(logging.INFO)
import importlib
import time
import sys
import objectsharer as objsh
from instrumentserver import pythonprocess

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
    logging.info(f'  Creating instrument {insname} of type {instype}')

    start = time.time()
    module_name = f'instrumentserver.instrument_plugins.{instype}'
    try:
        insmod = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name != module_name:
            raise
        sys.path.append('user_instruments')
        insmod = importlib.import_module(instype)
    insclass = getattr(insmod, instype, None)
    
    if insclass is None:
        raise ValueError('Instrument module does not contain instrument class')
    end = time.time()
    logging.debug(f'Loading instrument module {end - start:.03f} sec')

    logging.debug(f'Starting sharing server and connecting to {isrv}')
    if hasattr(objsh, 'ZMQBackend'):
        backend = objsh.ZMQBackend()
    else:
        backend = objsh.backend
    backend.start_server(addr='127.0.0.1')
    backend.connect_to(isrv)

    logging.debug(f'Creating instrument, name {insname}, kwargs {kwargs}')
    start = time.time()
    ins = insclass(insname, **kwargs)
    ins.set_remove_cb(close)
    end = time.time()
    logging.debug(f'Creating instrument took {end - start:.03f} sec')

    objsh.register(ins, name=insname)

    time.sleep(1)

    instruments = objsh.helper.find_object('instruments')
    ins.set_instruments(instruments)
    instruments.remove(insname)
    instruments.register_instrument(ins)
    backend.main_loop()
    ins.close()
