# Tests for SD1 import, device scanning, AWG signal playback, and digitizer setup.
# Hardware tests are parametrized over whatever scan() finds at runtime.

from __future__ import annotations

import logging
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# -- SD1 import ----------------------------------------------------------------
try:
    import instrumentserver.keysightAWG.keysightSD1 as key
    _SD1_AVAILABLE = True
except OSError:
    _SD1_AVAILABLE = False
    key = None

pytestmark = pytest.mark.skipif(
    not _SD1_AVAILABLE, reason="SD1core DLL not available"
)

# -- Discover hardware at collection time --------------------------------------
_scan_results: list[dict] = []
_awg_entries:  list[dict] = []
_dig_entries:  list[dict] = []

if _SD1_AVAILABLE:
    _scan_results = key.SD_Module.scan()
    _awg_entries = [
        m for m in _scan_results
        if m["type_enum"] == key.SD_Object_Type.AOU and m["open_status"] > 0
    ]
    _dig_entries = [
        m for m in _scan_results
        if m["type_enum"] == key.SD_Object_Type.AIN and m["open_status"] > 0
    ]


def _module_id(entry: dict) -> str:
    return f"{entry['product']}_ch{entry['chassis']}_sl{entry['slot']}"


# -- Import / symbol checks ----------------------------------------------------

def test_sd1_import():
    """keysightSD1 is importable and exposes all required symbols."""
    assert key is not None
    for name in ("SD_Module", "SD_AOU", "SD_AIN", "SD_Wave", "SD_Error",
                 "SD_Waveshapes", "SD_WaveformTypes", "SD_TriggerModes",
                 "AIN_Impedance", "AIN_Coupling"):
        assert hasattr(key, name), f"Missing symbol: {name}"


def test_error_codes_are_negative():
    assert key.SD_Error.OPENING_MODULE < 0
    assert key.SD_Error.MODULE_NOT_FOUND < 0
    assert key.SD_Error.MODULE_NOT_OPENED < 0


def test_trigger_mode_autotrig_is_zero():
    assert key.SD_TriggerModes.AUTOTRIG == 0


# -- Scan ----------------------------------------------------------------------

def test_scan_returns_list():
    """scan() returns a list regardless of whether hardware is present."""
    assert isinstance(_scan_results, list)


def test_scan_entry_keys():
    """Every scan() entry has all documented keys."""
    expected = {"index", "type_enum", "type_name", "product", "serial",
                "chassis", "slot", "open_status", "status",
                "fw_version", "hw_version", "self_test"}
    for entry in _scan_results:
        assert expected == set(entry.keys()), f"Key mismatch in entry: {entry}"


def test_scan_no_critical_firmware_warnings():
    """scan() must not emit CRITICAL log messages (firmware incompatibility).

    A CRITICAL from keysightSD1 means a module has firmware newer than what
    SD1 2.x supports and will malfunction.  Fail fast and surface the message.
    """
    sd1_logger = logging.getLogger("instrumentserver.keysightAWG.keysightSD1")

    class _CriticalCapture(logging.Handler):
        def __init__(self):
            super().__init__(logging.CRITICAL)
            self.records: list[logging.LogRecord] = []

        def emit(self, record: logging.LogRecord) -> None:
            self.records.append(record)

    handler = _CriticalCapture()
    sd1_logger.addHandler(handler)
    try:
        key.SD_Module.scan()
    finally:
        sd1_logger.removeHandler(handler)

    if handler.records:
        messages = "\n".join(r.getMessage() for r in handler.records)
        pytest.fail(f"SD1 CRITICAL firmware warning(s) detected:\n{messages}")


# -- AWG playback tests — one test case per discovered AWG ---------------------

@pytest.mark.parametrize("awg_entry", _awg_entries, ids=_module_id)
def test_awg_sawtooth_plays_and_isrunning(awg_entry):
    """For each discovered AWG: load a sawtooth, start, verify isRunning, stop, close."""
    product = awg_entry["product"]
    chassis = awg_entry["chassis"]
    slot    = awg_entry["slot"]
    channel = 1

    awg = key.SD_AOU()
    aou_id = awg.openWithSlot(product, chassis, slot)
    assert aou_id > 0, (
        f"openWithSlot({product}, {chassis}, {slot}) failed: "
        f"{key.SD_Error.getErrorMessage(aou_id)}"
    )

    try:
        array = np.zeros(1000)
        array[0] = -0.5
        for i in range(1, len(array)):
            array[i] = array[i - 1] + 0.001

        awg.channelAmplitude(channel, 0.1)
        awg.channelWaveShape(channel, key.SD_Waveshapes.AOU_AWG)
        awg.waveformFlush()
        awg.AWGflush(channel)

        wave = key.SD_Wave()
        rc = wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, array.tolist())
        assert rc >= 0, f"newFromArrayDouble failed: {rc}"

        rc = awg.waveformLoad(wave, 0)
        assert rc >= 0, f"waveformLoad failed: {rc}"

        awg.AWGqueueConfig(channel, 1)  # 1 = cyclic
        rc = awg.AWGqueueWaveform(channel, 0, key.SD_TriggerModes.SWHVITRIG, 0, 0, 0)
        assert rc >= 0, f"AWGqueueWaveform failed: {rc}"

        rc = awg.AWGstart(channel)
        assert rc >= 0, f"AWGstart failed: {rc}"

        rc = awg.AWGtrigger(channel)
        assert rc >= 0, f"AWGtrigger failed: {rc}"

        assert awg.AWGisRunning(channel), "AWG is not running after trigger"

        awg.AWGstop(channel)
        assert not awg.AWGisRunning(channel), "AWG still running after stop"

    finally:
        awg.AWGstopMultiple(0xF)
        awg.waveformFlush()
        awg.close()


# -- Digitizer tests — one test case per discovered digitizer ------------------

@pytest.mark.parametrize("dig_entry", _dig_entries, ids=_module_id)
def test_digitizer_daq_configure_and_stop(dig_entry):
    """For each discovered digitizer: open, configure channel + DAQ, start, stop, close.

    No signal is required — this verifies that all setup calls return without
    error codes and the DAQ engine starts and stops cleanly.
    """
    product = dig_entry["product"]
    chassis = dig_entry["chassis"]
    slot    = dig_entry["slot"]
    channel = 1
    n_samples = 1024
    n_cycles  = 10

    dig = key.SD_AIN()
    ain_id = dig.openWithSlot(product, chassis, slot)
    assert ain_id > 0, (
        f"openWithSlot({product}, {chassis}, {slot}) failed: "
        f"{key.SD_Error.getErrorMessage(ain_id)}"
    )

    try:
        dig.DAQstopMultiple(0xF)
        dig.DAQflushMultiple(0xF)

        rc = dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
        assert rc >= 0, f"triggerIOconfig failed: {rc}"

        rc = dig.channelInputConfig(
            channel, 2.0,
            key.AIN_Impedance.AIN_IMPEDANCE_50,
            key.AIN_Coupling.AIN_COUPLING_DC,
        )
        assert rc >= 0, f"channelInputConfig failed: {rc}"

        rc = dig.DAQconfig(channel, n_samples, n_cycles, 0, key.SD_TriggerModes.AUTOTRIG)
        assert rc >= 0, f"DAQconfig failed: {rc}"

        rc = dig.DAQstart(channel)
        assert rc >= 0, f"DAQstart failed: {rc}"

        data = dig.DAQread(channel, n_samples, timeOut=1000)
        assert len(data) == n_samples, (
            f"Expected {n_samples} samples, got {len(data)} "
            f"(digitizer may not be self-triggering or timed out)"
        )

        rc = dig.DAQstop(channel)
        assert rc >= 0, f"DAQstop failed: {rc}"

    finally:
        dig.DAQstopMultiple(0xF)
        dig.DAQflushMultiple(0xF)
        dig.close()
