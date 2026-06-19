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


def test_trg_io_line_goes_high_during_acquisition(dig, awg2):
    """Directly probe the TRG I/O connector's live logic level while AWG2's
    trigger pulse + HVI are running, bypassing DAQconfig/buffer-pool/clock
    entirely via trigger_io_read(). This isolates whether the external
    trigger signal (AWG2 ch1 -> DIG TRG I/O) is physically/electrically
    reaching the digitizer at all, independent of any acquisition-side bug.

    Bench wiring: the readout signal is generated from AWG3 ch6 and routes
    to Keysight DIG ch2 (unrelated to triggering). The trigger itself is
    AWG2 ch1 -> DIG TRG I/O. AWG2 ch1 here is a regular *analog* output
    channel repurposed as a pseudo-trigger, not AWG2's own dedicated
    Trigger In/Out connector -- if that channel's sequence queue never
    actually runs, also captured here via awg2.do_get_output(1), a
    queue-never-started bug can be told apart from a wrong-connector
    cabling issue without going to the bench first.
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

    PHYSICAL PRECONDITION: move the cable carrying AWG2 ch1's output from
    DIG TRG I/O to DIG channel 1 (free -- main_channel=2, ref_channel is
    NO_CHANNEL) before running this test.

    Uses a single AUTOTRIG capture sized to span one full HVI trigger
    period, rather than polling with repeated setup_raw_shot() calls --
    repeated reconfiguration without releasing the channel 1 buffer pool
    in between previously hung the test (DAQ_POOL_ALREADY_RUNNING / -8023
    on the 2nd call, since release_buf() only releases main/ref channel,
    never the explicit loopback channel passed here).
    """
    loopback_channel = 1

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
