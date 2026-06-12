# Tests for the Alazar ATSApi digitizer.
# Covers: DLL import, Constants, board discovery, configuration, and raw buffer capture.
# Hardware tests skip when no board is found.
# Capture uses AlazarForceTrigger so no external signal is required.

from __future__ import annotations

import ctypes
import logging
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# -- DLL / module availability ------------------------------------------------
_ATS_AVAILABLE = False
_alazar_mod = None

try:
    from lib.dll_support import alazar as _alazar_mod
    _ATS_AVAILABLE = True
except (OSError, ImportError):
    pass

pytestmark = pytest.mark.skipif(
    not _ATS_AVAILABLE, reason="ATSApi.dll not available"
)

AC  = _alazar_mod.Constants if _ATS_AVAILABLE else None
ats = _alazar_mod.ats       if _ATS_AVAILABLE else None

# -- Board discovery at collection time ---------------------------------------
_SYSTEM_ID = 1
_BOARD_ID  = 1

_board_handle = 0
if _ATS_AVAILABLE:
    _board_handle = ats.AlazarGetBoardBySystemID(_SYSTEM_ID, _BOARD_ID)

_BOARD_FOUND = bool(_board_handle)
skip_no_board = pytest.mark.skipif(not _BOARD_FOUND,
    reason=f"No Alazar board at system={_SYSTEM_ID} board={_BOARD_ID}")


# -- Import / symbol checks ---------------------------------------------------

def test_ats_module_imports():
    """lib.dll_support.alazar loads ATSApi.dll and exposes the expected objects."""
    assert _alazar_mod is not None
    assert hasattr(_alazar_mod, "ats")
    assert hasattr(_alazar_mod, "Constants")
    assert hasattr(_alazar_mod, "Alazar")
    assert hasattr(_alazar_mod, "CHK")


def test_ats_dll_has_required_functions():
    """ATSApi.dll exposes every function used by Alazar_Daemon."""
    required = [
        "AlazarGetBoardBySystemID",
        "AlazarGetStatus",
        "AlazarErrorToText",
        "AlazarInputControl",
        "AlazarSetBWLimit",
        "AlazarSetCaptureClock",
        "AlazarSetTriggerOperation",
        "AlazarSetExternalTrigger",
        "AlazarSetTriggerDelay",
        "AlazarBeforeAsyncRead",
        "AlazarSetRecordSize",
        "AlazarStartCapture",
        "AlazarAbortAsyncRead",
        "AlazarPostAsyncBuffer",
        "AlazarWaitAsyncBufferComplete",
        "AlazarGetChannelInfo",
        "AlazarGetParameter",
        "AlazarForceTrigger",
    ]
    for fn in required:
        assert hasattr(ats, fn), f"ATSApi.dll missing: {fn}"


def test_constants_channel_values():
    assert AC.CHANNEL_A == 1
    assert AC.CHANNEL_B == 2
    assert AC.CHANNEL_AB == 3


def test_constants_coupling_values():
    assert AC.COUPLING_AC == 1
    assert AC.COUPLING_DC == 2


def test_constants_sample_rate_ordering():
    """Higher SR_* constants must correspond to faster rates."""
    assert AC.SR_100M < AC.SR_250M < AC.SR_500M < AC.SR_1G


def test_constants_clock_sources_defined():
    for name in ("CLKSRC_INT", "CLKSRC_FASTEXT", "CLKSRC_SLOWEXT", "CLKSRC_EXT_10M"):
        assert hasattr(AC, name), f"Missing constant: {name}"


def test_chk_raises_on_non_512():
    """CHK must raise ValueError for any return code other than 512 (ApiSuccess)."""
    with pytest.raises(ValueError):
        _alazar_mod.CHK(0)
    with pytest.raises(ValueError):
        _alazar_mod.CHK(573)


def test_chk_passes_on_512():
    _alazar_mod.CHK(512)  # must not raise


# -- Board-level tests --------------------------------------------------------

@skip_no_board
def test_board_handle_is_nonzero():
    """AlazarGetBoardBySystemID returns a valid (non-zero) handle."""
    assert _board_handle != 0


@skip_no_board
def test_get_channel_info():
    """AlazarGetChannelInfo returns a plausible bits-per-sample and max-samples."""
    # AlazarGetChannelInfo expects two output pointers (ULONG*, BYTE*).
    # Do NOT use np.array(...).ctypes.data — that yields a Python int holding
    # the 64-bit memory address, which overflows the 32-bit register the DLL
    # expects, raising: ctypes.ArgumentError: OverflowError: int too long to convert.
    # ctypes.byref() produces a proper by-reference pointer at the right width.
    max_s = ctypes.c_uint32(0)
    bps   = ctypes.c_uint8(0)
    ret = ats.AlazarGetChannelInfo(
        _board_handle,
        ctypes.byref(max_s),
        ctypes.byref(bps),
    )
    assert ret == 512, f"AlazarGetChannelInfo failed: {ret}"
    assert bps.value in (8, 12, 14, 16), f"Unexpected bits per sample: {bps.value}"
    assert max_s.value > 0, "max_samples_per_record is 0"


@skip_no_board
def test_set_capture_clock_internal():
    """AlazarSetCaptureClock with internal 100 MHz returns ApiSuccess."""
    ret = ats.AlazarSetCaptureClock(
        _board_handle,
        AC.CLKSRC_INT,
        AC.SR_100M,
        AC.CLKEDG_RISE,
        0,
    )
    assert ret == 512, (
        f"AlazarSetCaptureClock failed: {ret} – {_alazar_mod.get_error(ret)}"
    )


@skip_no_board
def test_input_control_channel_a():
    """AlazarInputControl on channel A with 200 mV / DC / 50 Ω returns ApiSuccess."""
    ret = ats.AlazarInputControl(
        _board_handle,
        AC.CHANNEL_A,
        AC.COUPLING_DC,
        AC.RANGE_0200,
        AC.IMPEDANCE_50,
    )
    assert ret == 512, (
        f"AlazarInputControl failed: {ret} – {_alazar_mod.get_error(ret)}"
    )


@skip_no_board
def test_set_trigger_operation():
    """AlazarSetTriggerOperation with external trigger returns ApiSuccess."""
    ret = ats.AlazarSetTriggerOperation(
        _board_handle,
        AC.TRIG_ENGINE_OP_J,
        AC.TRIG_ENGINE_J, AC.TRIG_EXTERNAL, AC.TRIG_SLP_POS, 128,
        AC.TRIG_ENGINE_K, AC.TRIG_DISABLE,  AC.TRIG_SLP_POS, 128,
    )
    assert ret == 512, (
        f"AlazarSetTriggerOperation failed: {ret} – {_alazar_mod.get_error(ret)}"
    )


# -- Full buffer-capture test --------------------------------------------------

@skip_no_board
def test_raw_buffer_capture_with_force_trigger():
    """
    Full capture cycle using AlazarForceTrigger (no external signal required):
      - internal 100 MHz clock
      - channel A, 200 mV, DC, 50 Ω
      - 1024 samples / record, 1 record
      - AlazarForceTrigger fires the acquisition
      - assert the returned buffer has exactly 1024 samples
    """
    SAMPLES    = 1024
    REC_PER_BUF = 1
    REC_PER_ACQ = 1

    card = _alazar_mod.Alazar(systemid=_SYSTEM_ID, boardid=_BOARD_ID)
    card.set_capture_channels(AC.CHANNEL_A)
    card.set_ch_props(AC.CHANNEL_A, AC.RANGE_0200, AC.COUPLING_DC, AC.IMPEDANCE_50)

    # Internal 100 MHz clock
    ret = ats.AlazarSetCaptureClock(
        card.handle, AC.CLKSRC_INT, AC.SR_100M, AC.CLKEDG_RISE, 0
    )
    assert ret == 512, f"SetCaptureClock failed: {ret}"

    # External trigger at level 128 (will not fire on its own — we force it below)
    card.set_trigger_ext(128)

    # Determine bytes per sample.
    # Must use ctypes scalars + ctypes.byref(), not np.array().ctypes.data.
    # On 64-bit Windows, .ctypes.data returns a Python int equal to the full
    # 64-bit virtual address; passing that as a DLL argument overflows the
    # 32-bit output-pointer slot and raises an ArgumentError OverflowError.
    max_s = ctypes.c_uint32(0)
    bps   = ctypes.c_uint8(0)
    ats.AlazarGetChannelInfo(card.handle, ctypes.byref(max_s), ctypes.byref(bps))
    bytes_per_sample = (int(bps.value) + 7) // 8

    buf = np.zeros(SAMPLES * REC_PER_BUF * bytes_per_sample,
                   dtype=np.uint8 if bytes_per_sample == 1 else np.uint16)

    try:
        card.prepare_capture(SAMPLES, REC_PER_BUF, REC_PER_ACQ)
        card.post_buffers([buf])
        card.start_capture()

        # Fire a software trigger so the test runs without external hardware signal
        ats.AlazarForceTrigger(card.handle)

        data = card.get_next_buffer(timeout=1000)

    finally:
        card.end_capture()

    assert data is not None, (
        "get_next_buffer timed out — AlazarForceTrigger may not be supported "
        "on this board, or the board did not arm correctly"
    )
    assert len(data) == SAMPLES * bytes_per_sample, (
        f"Expected {SAMPLES * bytes_per_sample} raw bytes, got {len(data)}"
    )
