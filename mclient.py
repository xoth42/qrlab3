import sys
import os
import inspect
from lib import jsonext

import config
reload(config)

# Make sure we have our objectsharer and pulse sequencer in the path
srcdir = os.path.split(os.path.abspath(inspect.getsourcefile(lambda _: None)))[0]
for modname in 'objectsharer', 'pulseseq':
    pathname = os.path.join(srcdir, modname)
    if pathname not in sys.path:
        sys.path.insert(0, pathname)

import time
import objectsharer as objsh
#JOSH
#sequencer seems to depend on matplotlib, which depends on pyqt5 even though
# pyqt4 is installed. Probably a version of matplotlib that is too recent.
from pulseseq import sequencer, pulselib
#reload(sequencer)
#reload(pulselib)
import numpy as np
import types

import json
import matplotlib as mpl
import logging
mpl.rcParams['legend.fontsize'] = 9

# Set long call timeout because some AWG functions are slow
objsh.DEFAULT_TIMEOUT = 120000

if objsh.helper.backend is None:
    _zbe = objsh.ZMQBackend()
    _zbe.start_server(addr='127.0.0.1')
    sys.path.append(os.getcwd())

logging.debug('Connecting to instrument/data server...')
# 55555 = instrument, 55556 = data
for addr in ('tcp://127.0.0.1:55555', 'tcp://127.0.0.1:55556'):
    if addr not in objsh.helper.backend.addr_to_sock_map:
        print 'Connecting to %s' % (addr,)
        objsh.helper.backend.connect_to(addr)
        time.sleep(1)

instruments = objsh.helper.find_object('instruments')
datasrv = objsh.helper.find_object('dataserver')
##datafile = datasrv.get_file(config.datafilename)


def parse_chans(chans):
    if chans == '':
        return None
    chans = chans.split(',')
    ret = []
    for chan in chans:
        chan = chan.replace(' ','')
        try:
            ret.append(int(chan))
        except:
            ret.append(chan)
    return ret

class Container(object):
    pass

def get_container_object(name):
    qins = instruments.get(name)
    vals = qins.get_parameter_values()
    ret = Container()
    for k, v in vals.iteritems():
        setattr(ret, k, v)
    return ret

def get_qubit_info(name, detune=None):
    '''
    This function can be used to get an object that represents a qubit for
    the sequencer.

    It has the following properties:
    - rotate(<alpha>, <axis>): a rotation <alpha> around <axis>
    - ssb, side-band modulation object, call ssb.modulate()
    '''
    ret = get_container_object(name)
    ret.insname = name
    ret.channels = parse_chans(ret.channels)
    ret.sideband_channels = parse_chans(ret.sideband_channels)
    if ret.sideband_channels is None:
        ret.sideband_channels = ret.channels

    # Setup channels for this element. If no sideband modulation is used
    # (i.e. <deltaf> = 0), render directly into <channels>, otherwise to
    # <sideband_channels>
    df = ret.deltaf
    if detune:
        df += detune
    if df == 0:
        ret.ssb = None
        ret.sideband_channels = ret.channels
    else:
        period = 1e9 / df
        if ret.sideband_channels == ret.channels:
            replace = True
        else:
            replace = False
        ret.ssb = sequencer.SSB(period, ret.sideband_channels, ret.sideband_phase, outchans=ret.channels, replace=replace)

    # Setup rotation
    r = ret.rotation
    if type(r) is types.StringType:
        r = r.upper()
    if r == 'GAUSSIAN':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Gaussian, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    elif r == 'GAUSSIANSQUARE':
        ret.rotate = pulselib.GSRotation(ret.pi_amp, ret.w, ret.w, 0.0, 1.0, drag=ret.drag, chans=ret.sideband_channels)
    elif r == 'SQUARE':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Square, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    elif r == 'TRIANGLE':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Triangle, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    elif r == 'SINC':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Sinc, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    elif r == 'HANNING':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Hanning, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    elif r == 'KAISER':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Kaiser, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    else:
        ret.rotate = None

    
    # Setup rotation selective
    r = ret.rotation_selective
    if type(r) is types.StringType:
        r = r.upper()
    if r == 'GAUSSIAN':
        ret.rotate_selective = pulselib.AmplitudeRotation(pulselib.Gaussian, ret.w_selective, ret.pi_amp_selective, pi2_amp=ret.pi2_amp_selective, chans=ret.sideband_channels)
    elif r == 'GAUSSIANSQUARE':
        ret.rotate_selective = pulselib.GSRotation(ret.pi_amp_selective, ret.w_selective, ret.w_selective, 0.0, 1.0, chans=ret.sideband_channels)
    elif r == 'SQUARE':
        ret.rotate_selective = pulselib.AmplitudeRotation(pulselib.Square, ret.w_selective, ret.pi_amp_selective, pi2_amp=ret.pi2_amp_selective, chans=ret.sideband_channels)
    elif r == 'TRIANGLE':
        ret.rotate_selective = pulselib.AmplitudeRotation(pulselib.Triangle, ret.w_selective, ret.pi_amp_selective, pi2_amp=ret.pi2_amp_selective, chans=ret.sideband_channels)
    elif r == 'SINC':
        ret.rotate_selective = pulselib.AmplitudeRotation(pulselib.Sinc, ret.w_selective, ret.pi_amp_selective, pi2_amp=ret.pi2_amp_selective, chans=ret.sideband_channels)
    elif r == 'HANNING':
        ret.rotate_selective = pulselib.AmplitudeRotation(pulselib.Hanning, ret.w_selective, ret.pi_amp_selective, pi2_amp=ret.pi2_amp_selective, chans=ret.sideband_channels)
    elif r == 'KAISER':
        ret.rotate_selective = pulselib.AmplitudeRotation(pulselib.Kaiser, ret.w_selective, ret.pi_amp_selective, pi2_amp=ret.pi2_amp_selective, chans=ret.sideband_channels)
    else:
        ret.rotate_selective = None

    # Setup rotation quasi-selective
    r = ret.rotation_quasilective
    if type(r) is types.StringType:
        r = r.upper()
    if r == 'GAUSSIAN':
        ret.rotate_quasilective = pulselib.AmplitudeRotation(pulselib.Gaussian, ret.w_quasilective, ret.pi_amp_quasilective, pi2_amp=ret.pi2_amp_quasilective, chans=ret.sideband_channels)
    elif r == 'GAUSSIANSQUARE':
        ret.rotate_quasilective = pulselib.GSRotation(ret.pi_amp_quasilective, ret.w_quasilective, ret.w_quasilective, 0.0, 1.0, chans=ret.sideband_channels)
    elif r == 'SQUARE':
        ret.rotate_quasilective = pulselib.AmplitudeRotation(pulselib.Square, ret.w_quasilective, ret.pi_amp_quasilective, pi2_amp=ret.pi2_amp_quasilective, chans=ret.sideband_channels)
    elif r == 'TRIANGLE':
        ret.rotate_quasilective = pulselib.AmplitudeRotation(pulselib.Triangle, ret.w_quasilective, ret.pi_amp_quasilective, pi2_amp=ret.pi2_amp_quasilective, chans=ret.sideband_channels)
    elif r == 'SINC':
        ret.rotate_quasilective = pulselib.AmplitudeRotation(pulselib.Sinc, ret.w_quasilective, ret.pi_amp_quasilective, pi2_amp=ret.pi2_amp_quasilective, chans=ret.sideband_channels)
    elif r == 'HANNING':
        ret.rotate_quasilective = pulselib.AmplitudeRotation(pulselib.Hanning, ret.w_quasilective, ret.pi_amp_quasilective, pi2_amp=ret.pi2_amp_quasilective, chans=ret.sideband_channels)
    elif r == 'KAISER':
        ret.rotate_quasilective = pulselib.AmplitudeRotation(pulselib.Kaiser, ret.w_quasilective, ret.pi_amp_quasilective, pi2_amp=ret.pi2_amp_quasilective, chans=ret.sideband_channels)
    else:
        ret.rotate_quasilective = None
    

    if ret.marker_channel is not None and ret.marker_channel != '':
        ret.marker = dict(channel=ret.marker_channel, bufwidth=ret.marker_bufwidth, ofs=ret.marker_ofs)
    else:
        ret.marker = None

    return ret

def get_gate_info(name, detune=None):
    '''
    This function can be used to get an object that represents a qubit for
    the sequencer.

    It has the following properties:
    - rotate(<alpha>, <axis>): a rotation <alpha> around <axis>
    - ssb, side-band modulation object, call ssb.modulate()
    '''
    ret = get_container_object(name)
    ret.insname = name
    ret.channels = parse_chans(ret.channels)
    ret.sideband_channels = parse_chans(ret.sideband_channels)
    ret.channels2 = parse_chans(ret.channels2)
    ret.sideband_channels2 = parse_chans(ret.sideband_channels2)
    if ret.sideband_channels is None:
        ret.sideband_channels = ret.channels
    if ret.sideband_channels2 is None:
        ret.sideband_channels2 = ret.channels2

    # Setup channels for this element. If no sideband modulation is used
    # (i.e. <deltaf> = 0), render directly into <channels>, otherwise to
    # <sideband_channels>
    df = ret.deltaf
    rel_amp = ret.relative_amp
    rel_phase = ret.relative_phase
    if detune:
        df += detune
    if df == 0:
        ret.ssb = None
        ret.sideband_channels = ret.channels
        ret.sideband_channels2 = ret.channels2        
    else:
        period = 1e9 / df
        if ret.sideband_channels == ret.channels:
            replace = True
        else:
            replace = False
        ssb1 = sequencer.SSB(period, ret.sideband_channels, ret.sideband_phase, outchans=ret.channels, replace=replace)
        if ret.sideband_channels2 == ret.channels2:
            replace = True
        else:
            replace = False
        ssb2 = sequencer.SSB(period, ret.sideband_channels2, ret.sideband_phase2, outchans=ret.channels2, replace=replace)
        ret.ssb_list = [ssb1,ssb2]

    # Setup rotation
    r = ret.rotation
    if type(r) is types.StringType:
        r = r.upper()
            
    if r == 'GAUSSIAN':
        ret.rotate = pulselib.CombinedAmplitudeRotation(pulselib.Gaussian, ret.w, ret.pi_amp, rel_amp, rel_phase, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels, chans2=ret.sideband_channels2)
    elif r == 'GAUSSIANSQUARE':
        ret.rotate = pulselib.CombinedGSRotation(ret.sq_len, ret.pi_amp, ret.w, rel_amp, rel_phase, drag=ret.drag, chop=ret.chop, chans=ret.sideband_channels, chans2=ret.sideband_channels2)
    elif r == 'SQUARE':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Square, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    elif r == 'TRIANGLE':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Triangle, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    elif r == 'SINC':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Sinc, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    elif r == 'HANNING':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Hanning, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    elif r == 'KAISER':
        ret.rotate = pulselib.AmplitudeRotation(pulselib.Kaiser, ret.w, ret.pi_amp, drag=ret.drag, pi2_amp=ret.pi2_amp, chans=ret.sideband_channels)
    else:
        ret.rotate = None

    if ret.marker_channel is not None and ret.marker_channel != '':
        ret.marker = dict(channel=ret.marker_channel, bufwidth=ret.marker_bufwidth, ofs=ret.marker_ofs)
    else:
        ret.marker = None

    return ret

def get_qubits():
    qs = {}
    l = instruments.list_instruments()
    for name in l:
        if not name.startswith('qubit'):
            continue
        qname = name[5:]
        info = get_qubit_info(name)
        try:
            qs[int(qname)] = info
        except:
            qs[qname] = info
    return qs

def get_readout_info(readout='readout'):
    ret = get_container_object(readout)
    if readout is 'readout_IQ': # JEFF- changed to get IQ readout working
        ret.rfsource = instruments.get(ret.rfsource)
        return ret
    ret.rfsource1 = instruments.get(ret.rfsource1)
    ret.rfsource2 = instruments.get(ret.rfsource2)
    return ret

def object_hook(obj):
    if '__complex__' in obj:
        return obj['re']+1j*obj['im']
    else:
        return obj

def load_settings_from_file(fn, inslist):
    '''
    Load instrument settings from file <fn>.
    inslist is a list of instrument names for which to apply the settings.
    If <inslist> is 'all' the settings for all instruments in the file will be
    loaded.
    '''

    f = open(fn)
    settings = json.load(f, object_hook=object_hook)
    if inslist == 'all':
        inslist = settings.keys()
    for insname in inslist:
        print '%s:' % (insname,)
        if insname not in settings:
            print '    No settings available'
            continue
        ins = instruments[insname]
        if ins is None:
            print '    Instrument not present'
            continue
        for key, val in settings[insname].iteritems():
            print '    Setting %s to %s' % (key, val)
            if type(val) is types.UnicodeType:
                val = str(val)
            ins.set(str(key), val)

def get_temp_file():
    return datasrv.get_file(config.tempfilename)

def remove_temp_file():
    logging.info('Removing temp file from dataserver')
    try:
        tmp = get_temp_file()
        name = tmp.get_fullname()
        tmp.close()
        os.remove(config.tempfilename)
    except Exception, e:
        logging.warning('Failed to remove temporary file: %s' % str(e))
        pass

def save_instruments(fn=config.ins_store_fn):
    '''
    Save instrument settings for later use, by default in <ins_store_fn>.
    '''
    settings = instruments.get_all_parameters()
    with open(fn, "w") as sfile:
        jsonext.dump(settings, sfile)

def restore_instruments(fn=config.ins_store_fn):
    '''
    Restore previously saved instrument settings.
    '''
    load_settings_from_file(fn, 'all')

instruments = objsh.helper.find_object('instruments')
datasrv = objsh.helper.find_object('dataserver')
datadir = 'c:/_data'


filename = 'c:/_data/01052021cooldown_circulator.hdf5'




datafile = datasrv.get_file(filename)
