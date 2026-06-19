# Hardware-in-the-loop test for isolating the EXTTRIG/TRG-I/O detection bug
# on the Keysight M3102A digitizer (channel_delay=0, naverages=1 raw shots
# kept returning empty buffers even after the buffer-pool NULL-pointer fix
# and the triggerIOconfig missing-syncMode fix in keysightSD1.py).
#
# Assumes create_instruments.py has already been run, i.e. the instrument
# server is up and 'dig', 'AWG2', 'AWG3', 'readout_IQ' already exist.
# Run with: pytest test/test_keysight_trigger.py -s

import os
import sys
import time

import numpy as np
import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from mclient import instruments  # noqa: E402
from scripts.single_cavity.readout_window_delay_sweep import \
    ReadoutWindowDelaySweep  # noqa: E402


@pytest.fixture
def dig():
    return instruments['dig']


@pytest.fixture
def awg2():
    return instruments['AWG2']


@pytest.fixture
def awg3():
    return instruments['AWG3']


def test_trg_io_line_goes_high_during_acquisition(dig, awg2):
    """Directly probe the TRG I/O connector's live logic level while AWG2's
    trigger pulse + HVI are running, bypassing DAQconfig/buffer-pool/clock
    entirely via trigger_io_read(). This isolates whether the external
    trigger signal is physically/electrically reaching the digitizer at
    all, independent of any acquisition-side bug.

    Bench wiring (TESTING_TRIGGER setup): AWG2 ch1 -> DIG ch1 carries the
    pulse for visualization (the permanent main signal path, main_channel=1
    -- see test_awg2_ch1_loopback_pulse_shape). Triggering itself now goes
    through AWG2's own dedicated Trigger Out connector -> DIG Trigger In
    (configured via Keysight_AWG's trigger_io_mode="out"), not through an
    analog channel repurposed as a pseudo-trigger. awg2.do_get_output(1) is
    still sampled here as a sanity check that AWG2 ch1's own queue is
    running, even though it's no longer the trigger source.

    """
    # setup_raw_shot calls triggerIOconfig(AOU_TRG_IN, ...), which puts the
    # TRG I/O connector in input mode -- required for trigger_io_read() to
    # reflect the external line rather than an output we'd be driving.
    dig.setup_raw_shot(naverages=1)

    m = ReadoutWindowDelaySweep(delays=np.array([0, 1]), readout='readout_IQ')
    m.stop_awgs()
    m.load(m.generate())
    m.start_awgs()

    dig.arm()
    dig.start_hvi()

    trg_samples = []
    awg2_ch1_running = []
    deadline = time.time() + 1.0
    while time.time() < deadline:
        trg_samples.append(dig.trigger_io_read())
        awg2_ch1_running.append(awg2.do_get_output(1))
        time.sleep(0.01)

    dig.stop_hvi()
    m.stop_awgs()
    dig.release_buf()

    print("trigger_io_read samples:", trg_samples)
    print("AWG2 ch1 running (AWGisRunning) samples:", awg2_ch1_running)

    assert any(s != 0 for s in trg_samples), (
        "TRG I/O line never read nonzero while AWG2/HVI were running "
        f"(trg_samples={trg_samples}, awg2_ch1_running={awg2_ch1_running}); "
        "if awg2_ch1_running is also all-falsy, AWG2 ch1's sequence queue "
        "never started playing at all (a software/sequence-gating bug, not "
        "cabling). If awg2_ch1_running is truthy throughout, AWG2 ch1 is "
        "actively playing back but the pulse isn't reaching the connector "
        "-- check whether the cable should be on AWG2's dedicated Trigger "
        "In/Out port instead of its ch1 analog output."
    )


def test_awg2_ch1_loopback_pulse_shape(dig):
    """Capture AWG2 ch1's actual analog output directly on a digitizer ADC
    channel, instead of reading it indirectly through the TRG I/O digital
    input. Settles whether AWG2 ch1 is really producing a pulse at all
    (vs. stuck on a SWHVITRIG-gated zero segment inside its own queue,
    despite reporting AWGisRunning()=1) -- independent of any TRG I/O
    connector/cabling question.

    Uses dig.get_main_channel() rather than a hardcoded channel: in the
    TESTING_TRIGGER bench setup, AWG2 ch1 -> DIG ch1 is the permanent main
    signal path (main_channel=1), not a temporary loopback onto a free
    channel.

    Uses a single AUTOTRIG capture sized to span one full HVI trigger
    period, rather than polling with repeated setup_raw_shot() calls --
    repeated reconfiguration without releasing the channel's buffer pool
    in between previously hung the test (DAQ_POOL_ALREADY_RUNNING / -8023
    on the 2nd call, since release_buf() only releases main/ref channel,
    never an explicit channel passed to setup_raw_shot directly).
    """
    loopback_channel = dig.get_main_channel()

    # Span a full trigger period (with margin) so the pulse is guaranteed
    # to fall inside a single capture window regardless of timing offset.
    sample_rate = dig.get_sample_rate()
    trigger_period_s = dig.get_trigger_period() * 1e-6
    if_period = dig.get_if_period()
    nsamples = int(trigger_period_s * sample_rate * 1.5)
    nsamples -= nsamples % if_period  # DAQconfig requires nsamples % if_period == 0

    m = ReadoutWindowDelaySweep(delays=np.array([0, 1]), readout='readout_IQ')
    m.stop_awgs()
    m.load(m.generate())
    m.start_awgs()

    dig.start_hvi()  # let AWG2's sequence actually run/advance
    time.sleep(0.1)  # make sure AWG2 is already mid-loop before we arm

    # AUTOTRIG: digitizer captures immediately, no trigger of its own
    # needed -- only AWG2's own queue/HVI gating is under test here.
    dig.set_nsamples(nsamples)
    dig.setup_raw_shot(channel=loopback_channel, naverages=1, ntransfers=1, triggermode=0)
    dig.arm()
    raw = dig.take_raw_shot(channel=loopback_channel)
    dig.release_buf()

    dig.stop_hvi()
    m.stop_awgs()

    assert len(raw) > 0, (
        "AUTOTRIG capture on DIG ch1 returned no data at all -- check "
        "the loopback cable is actually connected to DIG ch1."
    )

    span = float(np.max(raw) - np.min(raw))
    print("AWG2 ch1 loopback capture (%d samples) peak-to-peak span: %.1f" % (len(raw), span))

    # Pure ADC noise floor measured ~40 counts peak-to-peak (see AUTOTRIG
    # sanity check). A real ~1.5V pulse at VOLTAGE_SCALE=2.8V full-scale on
    # a 14-bit ADC would swing thousands of counts -- 500 safely separates
    # "real pulse" from "noise only".
    assert span > 500, (
        f"AWG2 ch1 loopback into DIG ch1 never showed pulse structure above "
        f"the noise floor (peak-to-peak span={span}); AWG2 ch1's analog "
        "output is not producing a pulse at all, despite AWGisRunning()=1 "
        "-- likely stuck on a SWHVITRIG-gated zero segment inside its own "
        "queue (an HVI/sequence issue), not a connector mismatch."
    )


def test_awg2_ch1_free_run_analog_path(dig, awg2):
    """Definitive analog-path test, isolated from the sequencer/HVI/SWHVITRIG.

    free_run_pulse() makes AWG2 ch1 continuously loop a square pulse with no
    trigger gating, so the pulse is always present -- an AUTOTRIG digitizer
    capture is guaranteed to land on it regardless of the millisecond-scale
    proxy latency that makes a single arm-then-trigger sequence unreliable
    (the AUTOTRIG capture window is only ~150us). If THIS shows a real swing,
    the AWG ch1 -> DIG ch1 analog path is healthy and the remaining problem
    is purely how the normal sequence's pulse gets triggered (HVI/SWHVITRIG),
    not the DAQ buffer, the ADC, or the cabling.
    """
    capture_channel = dig.get_main_channel()

    sample_rate = dig.get_sample_rate()
    if_period = dig.get_if_period()
    nsamples = int(sample_rate * 100e-6)  # ~100us window
    nsamples -= nsamples % if_period

    awg2.stop()
    awg2.free_run_pulse(channel=1, length=2000, amp=0.9)
    time.sleep(0.1)  # let the free-running loop settle

    dig.set_nsamples(nsamples)
    dig.setup_raw_shot(channel=capture_channel, naverages=1, ntransfers=1, triggermode=0)
    dig.arm()
    raw = dig.take_raw_shot(channel=capture_channel)
    dig.release_buf()

    awg2.stop()

    assert len(raw) > 0, "AUTOTRIG capture on DIG returned no data at all."

    span = float(np.max(raw) - np.min(raw))
    print("AWG2 ch1 free-run capture (%d samples) peak-to-peak span: %.1f" % (len(raw), span))

    assert span > 500, (
        f"AWG2 ch1 free-running square pulse never appeared on DIG "
        f"(peak-to-peak span={span}, noise floor ~40-90). With the pulse "
        "free-running continuously, AUTOTRIG must catch it -- if it doesn't, "
        "the AWG ch1 -> DIG ch1 analog path itself is broken (cable, wrong "
        "connector, or channel not actually outputting), NOT a trigger/HVI "
        "timing issue."
    )


def test_awg2_triggered_pulses(dig, awg2):
    """Trigger-based version of the free-run analog test: AWG2 ch1 emits N
    pulses, and at the start of each pulse AWG2's own front-panel Trigger Out
    fires a marker (AWGqueueMarkerConfig markerMode=2). With AWG2 TRG OUT
    wired to DIG TRG IN and AWG2 ch1 wired to DIG ch1, the digitizer captures
    N EXTTRIG-triggered shots, each of which should contain the pulse.

    This is the non-HVI trigger path: instead of the HVI distributing the
    digitizer trigger, the AWG itself emits a hardware trigger synchronized
    to its analog pulse. Proves AWG2 ch1 -> DIG ch1 (signal) + AWG2 TRG OUT
    -> DIG TRG IN (trigger) work together end to end.
    """
    N = 10
    capture_channel = dig.get_main_channel()  # DIG ch1 in TESTING_TRIGGER

    # AWG2 ch1 free-running pulse, length samples at 1 GS/s. Keep the DIG
    # capture window to roughly half the AWG loop period so each triggered
    # shot fits inside one loop iteration.
    awg_pulse_len = 4000  # 4 us loop at 1 GS/s
    sample_rate = dig.get_sample_rate()  # DIG, ~500 MS/s
    if_period = dig.get_if_period()
    nsamples = int(0.5 * awg_pulse_len * 1e-9 * sample_rate)  # ~half the loop
    nsamples -= nsamples % if_period

    awg2.stop()
    awg2.free_run_pulse(channel=1, length=awg_pulse_len, amp=0.9, trigger_out=True)
    time.sleep(0.1)  # let the free-running loop settle

    dig.set_nsamples(nsamples)
    dig.set_naverages(N)
    # Default triggermode is EXTTRIG -- capture N shots, each gated by an
    # AWG2 TRG OUT marker edge arriving at DIG TRG IN.
    dig.setup_raw_shot(channel=capture_channel, naverages=N, ntransfers=1)
    dig.arm()
    raw = dig.take_raw_shot(channel=capture_channel)
    dig.release_buf()

    awg2.stop()

    assert len(raw) == N * nsamples, (
        f"Expected {N} triggered shots of {nsamples} samples "
        f"({N * nsamples} total), got {len(raw)} -- fewer triggers arrived "
        "than requested, so AWG2 TRG OUT -> DIG TRG IN is not delivering one "
        "edge per pulse."
    )

    shots = raw.reshape(N, nsamples)
    spans = [float(s.max() - s.min()) for s in shots]
    print("AWG2 triggered-pulse per-shot peak-to-peak spans:", spans)

    assert all(span > 500 for span in spans), (
        f"Not all {N} EXTTRIG-triggered shots contained the pulse "
        f"(spans={spans}, noise floor ~40-90). Each AWG2 TRG OUT edge should "
        "trigger a capture window that lands on the synchronized ch1 pulse."
    )


def test_non_hvi_free_run_real_sequence(dig, awg2, awg3):
    """Patch the AWGs into non-HVI (use_hvi=False) mode and verify the *real*
    readout sequence pulse free-runs onto the digitizer.

    This is the proof-of-concept for the non-HVI sequencing approach: instead
    of the normal SWHVITRIG-gated first element waiting on an HVI trigger that
    is never re-fired per cycle (see project_keysight_dig_bugs_fixed), every
    element becomes AUTOTRIG so the cyclic queue loops the real pulse
    continuously. Unlike test_awg2_ch1_free_run_analog_path (a synthetic
    square wave), this exercises the actual ReadoutWindowDelaySweep sequence
    end to end -- only the trigger gating differs.

    Restores use_hvi=True afterward so the toggle doesn't leak to other tests.
    """
    capture_channel = dig.get_main_channel()

    prev_use_hvi = (awg2.get_use_hvi(), awg3.get_use_hvi())
    try:
        awg2.set_use_hvi(False)
        awg3.set_use_hvi(False)

        sample_rate = dig.get_sample_rate()
        if_period = dig.get_if_period()
        nsamples = int(sample_rate * 100e-6)  # ~100us window
        nsamples -= nsamples % if_period

        # Load + start the normal sequence; with use_hvi=False it free-runs.
        m = ReadoutWindowDelaySweep(delays=np.array([0, 1]), readout='readout_IQ')
        m.stop_awgs()
        m.load(m.generate())
        m.start_awgs()
        time.sleep(0.1)  # let the free-running loop settle

        # No HVI needed -- the cyclic AUTOTRIG queue is already looping.
        dig.set_nsamples(nsamples)
        dig.setup_raw_shot(channel=capture_channel, naverages=1, ntransfers=1, triggermode=0)
        dig.arm()
        raw = dig.take_raw_shot(channel=capture_channel)
        dig.release_buf()

        m.stop_awgs()
    finally:
        awg2.set_use_hvi(prev_use_hvi[0])
        awg3.set_use_hvi(prev_use_hvi[1])

    assert len(raw) > 0, "AUTOTRIG capture on DIG returned no data at all."

    span = float(np.max(raw) - np.min(raw))
    print("non-HVI real-sequence capture (%d samples) peak-to-peak span: %.1f" % (len(raw), span))

    assert span > 500, (
        f"The real readout sequence in non-HVI (free-run) mode never produced "
        f"a pulse on DIG (peak-to-peak span={span}, noise floor ~40-90). "
        "Expected: with use_hvi=False every element is AUTOTRIG so the cyclic "
        "queue loops the pulse continuously and AUTOTRIG capture catches it."
    )
