import sys
import os
from lib import jsonext

import config
import importlib
import time
import objectsharer as objsh
from pulseseq import sequencer, pulselib

import json
import matplotlib as mpl
import logging

importlib.reload(config)

mpl.rcParams["legend.fontsize"] = 9

# * Highlight
filename = 'c:/_data/test.hdf5'

# Set long call timeout because some AWG functions are slow
objsh.DEFAULT_TIMEOUT = 120000

if objsh.helper.backend is None:
    _zbe = objsh.ZMQBackend()
    _zbe.start_server(addr="127.0.0.1")
    sys.path.append(os.getcwd())

logging.debug("Connecting to instrument/data server...")
for addr in ("tcp://127.0.0.1:55555", "tcp://127.0.0.1:55556"):
    if addr not in objsh.helper.backend.addr_to_sock_map:
        print(f"Connecting to {addr}")
        objsh.helper.backend.connect_to(addr)
        time.sleep(1)

instruments = objsh.helper.find_object("instruments")
datasrv = objsh.helper.find_object("dataserver")

datafile = datasrv.get_file(filename)


def parse_chans(chans):
    """Normalize a comma-separated channel list into integers and strings."""
    if chans == "":
        return None
    parsed = []
    for chan in chans.split(","):
        chan = chan.strip()
        if chan == "":
            continue
        try:
            parsed.append(int(chan))
        except ValueError:
            parsed.append(chan)
    return parsed


def _normalize_text(value):
    """Return text for config-backed values that may arrive as bytes."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode()
    return value


_ROTATION_WAVEFORMS = {
    "GAUSSIAN": pulselib.Gaussian,
    "SQUARE": pulselib.Square,
    "TRIANGLE": pulselib.Triangle,
    "SINC": pulselib.Sinc,
    "HANNING": pulselib.Hanning,
    "KAISER": pulselib.Kaiser,
}


def _rotation_mode(value):
    """Return a canonical rotation mode string."""
    return _normalize_text(value).upper()


def _build_single_rotation(
    mode, width, pi_amp, chans, drag=None, pi2_amp=None
):
    """Build a single-channel pulse-shape rotation from a mode name."""
    if mode == "GAUSSIANSQUARE":
        return pulselib.GSRotation(
            pi_amp, width, width, 0.0, 1.0, drag=drag, chans=chans
        )

    waveform = _ROTATION_WAVEFORMS.get(mode)
    if waveform is None:
        return None
    return pulselib.AmplitudeRotation(
        waveform,
        width,
        pi_amp,
        drag=drag,
        pi2_amp=pi2_amp,
        chans=chans,
    )


def _build_combined_rotation(
    mode,
    width,
    pi_amp,
    rel_amp,
    rel_phase,
    chans,
    chans2,
    drag=None,
    pi2_amp=None,
    chop=None,
    sq_len=None,
):
    """Build the two-channel rotation used by gate definitions."""
    if mode == "GAUSSIANSQUARE":
        return pulselib.CombinedGSRotation(
            sq_len,
            pi_amp,
            width,
            rel_amp,
            rel_phase,
            drag=drag,
            chop=chop,
            chans=chans,
            chans2=chans2,
        )

    waveform = _ROTATION_WAVEFORMS.get(mode)
    if waveform is None:
        return None
    return pulselib.CombinedAmplitudeRotation(
        waveform,
        width,
        pi_amp,
        rel_amp,
        rel_phase,
        drag=drag,
        pi2_amp=pi2_amp,
        chans=chans,
        chans2=chans2,
    )


class Container(object):
    pass


def get_container_object(name):
    qins = instruments.get(name)
    vals = qins.get_parameter_values()
    ret = Container()
    for k, v in vals.items():
        setattr(ret, k, v)
    return ret


def get_qubit_info(name, detune=None):
    """
    This function can be used to get an object that represents a qubit for
    the sequencer.

    It has the following properties:
    - rotate(<alpha>, <axis>): a rotation <alpha> around <axis>
    - ssb, side-band modulation object, call ssb.modulate()
    """
    ret = get_container_object(name)
    ret.insname = name
    ret.channels = parse_chans(ret.channels)
    ret.sideband_channels = parse_chans(ret.sideband_channels)
    if ret.sideband_channels is None:
        ret.sideband_channels = ret.channels
    # Preserve the special fixed phase used by the readout_IQ configuration.
    fixed_phase = None
    if name == "readout_IQ":
        fixed_phase = ret.fixed_phase

    # If no sideband modulation is needed, render directly on the output
    # channels. Otherwise build an SSB wrapper that renders into the sideband
    # channels first and routes the result to the outputs.
    df = ret.deltaf
    if detune:
        df += detune
    if df == 0:
        ret.ssb = None
        ret.sideband_channels = ret.channels
    else:
        period = 1e9 / df
        ret.ssb = sequencer.SSB(
            period,
            ret.sideband_channels,
            ret.sideband_phase,
            outchans=ret.channels,
            replace=(ret.sideband_channels == ret.channels),
            fixed_phase=fixed_phase,
        )

    # Build the pulse-shape helpers that callers use when composing sequences.
    ret.rotate = _build_single_rotation(
        _rotation_mode(ret.rotation),
        ret.w,
        ret.pi_amp,
        ret.sideband_channels,
        drag=ret.drag,
        pi2_amp=ret.pi2_amp,
    )
    ret.rotate_selective = _build_single_rotation(
        _rotation_mode(ret.rotation_selective),
        ret.w_selective,
        ret.pi_amp_selective,
        ret.sideband_channels,
        pi2_amp=ret.pi2_amp_selective,
    )
    ret.rotate_quasilective = _build_single_rotation(
        _rotation_mode(ret.rotation_quasilective),
        ret.w_quasilective,
        ret.pi_amp_quasilective,
        ret.sideband_channels,
        pi2_amp=ret.pi2_amp_quasilective,
    )

    if ret.marker_channel is not None and ret.marker_channel != "":
        ret.marker = dict(
            channel=ret.marker_channel,
            bufwidth=ret.marker_bufwidth,
            ofs=ret.marker_ofs,
        )
    else:
        ret.marker = None

    return ret


def get_gate_info(name, detune=None):
    """
    This function can be used to get an object that represents a qubit for
    the sequencer.

    It has the following properties:
    - rotate(<alpha>, <axis>): a rotation <alpha> around <axis>
    - ssb, side-band modulation object, call ssb.modulate()
    """
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

    # Gate definitions use two related channel sets. We only build the SSB
    # wrappers when a non-zero detuning requires modulation.
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
        ret.ssb_list = [
            sequencer.SSB(
                period,
                ret.sideband_channels,
                ret.sideband_phase,
                outchans=ret.channels,
                replace=(ret.sideband_channels == ret.channels),
            ),
            sequencer.SSB(
                period,
                ret.sideband_channels2,
                ret.sideband_phase2,
                outchans=ret.channels2,
                replace=(ret.sideband_channels2 == ret.channels2),
            ),
        ]

    # The combined gate helpers use the same mode mapping plus the relative
    # amplitude and phase needed to shape both channels together.
    ret.rotate = _build_combined_rotation(
        _rotation_mode(ret.rotation),
        ret.w,
        ret.pi_amp,
        rel_amp,
        rel_phase,
        ret.sideband_channels,
        ret.sideband_channels2,
        drag=ret.drag,
        pi2_amp=ret.pi2_amp,
        chop=ret.chop,
        sq_len=ret.sq_len,
    )

    if ret.marker_channel is not None and ret.marker_channel != "":
        ret.marker = dict(
            channel=ret.marker_channel,
            bufwidth=ret.marker_bufwidth,
            ofs=ret.marker_ofs,
        )
    else:
        ret.marker = None

    return ret


def get_qubits():
    qs = {}
    instrument_names = instruments.list_instruments()
    for name in instrument_names:
        if not name.startswith("qubit"):
            continue
        qname = name[5:]
        info = get_qubit_info(name)
        try:
            qs[int(qname)] = info
        except ValueError:
            qs[qname] = info
    return qs


def get_readout_info(readout="readout"):
    ret = get_container_object(readout)
    if readout == "readout_IQ":  # JEFF- changed to get IQ readout working
        ret.rfsource = instruments.get(ret.rfsource)
        return ret
    ret.rfsource1 = instruments.get(ret.rfsource1)
    ret.rfsource2 = instruments.get(ret.rfsource2)
    return ret


def object_hook(obj):
    if obj.get("__complex__"):
        return obj["re"] + 1j * obj["im"]
    return obj


def load_settings_from_file(fn, inslist):
    """
    Load instrument settings from file <fn>.
    inslist is a list of instrument names for which to apply the settings.
    If <inslist> is 'all' the settings for all instruments in the file will be
    loaded.
    """

    with open(fn) as f:
        settings = json.load(f, object_hook=object_hook)
    if inslist == "all":
        inslist = list(settings.keys())
    for insname in inslist:
        print(f"{insname}:")
        if insname not in settings:
            print("    No settings available")
            continue
        ins = instruments[insname]
        if ins is None:
            print("    Instrument not present")
            continue
        for key, val in settings[insname].items():
            print(f"    Setting {key} to {val}")
            if isinstance(val, bytes):
                val = val.decode()
            ins.set(str(key), val)


def get_temp_file():
    return datasrv.get_file(config.tempfilename)


def remove_temp_file():
    logging.info("Removing temp file from dataserver")
    try:
        tmp = get_temp_file()
        tmp.close()
        os.remove(config.tempfilename)
    except Exception as exc:
        logging.warning(f"Failed to remove temporary file: {exc}", )


def save_instruments(fn=config.ins_store_fn):
    """
    Save instrument settings for later use, by default in <ins_store_fn>.
    """
    settings = instruments.get_all_parameters()
    with open(fn, "w") as sfile:
        jsonext.dump(settings, sfile)


def restore_instruments(fn=config.ins_store_fn):
    """
    Restore previously saved instrument settings.
    """
    load_settings_from_file(fn, "all")
