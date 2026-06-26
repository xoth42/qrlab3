# HVI / SD1 2.x Notes

Working notes on triggering the Keysight M3202A AWGs and M3102A digitizer
through the SD1 2.x libraries. Some of this is **confirmed on the bench**;
the rest is **speculation** flagged as such. Treat it as a lab notebook, not
a spec.

## Bench wiring (current)

- **AWG2 ch1 → DIG ch1** — analog signal path into the digitizer ADC.
- **AWG2 TRG OUT → DIG TRG IN** — a physical front-panel trigger wire.

## The two trigger paths in the code

There are two *separate, unconnected* ways the readout gets triggered, and
mixing them up causes most of the confusion:

1. **HVI / co-fired path** (`measure()`, `show_pulse()`).
   `dig.start_hvi()` runs a precompiled `2slot100us.HVI` binary that drives an
   internal **SWHVITRIG** signal over the PXI backplane. `acq_chan="1m1"` in
   `Readout_IQ_Info` only marks an AWG queue element as SWHVITRIG-gated — it
   controls *when an AWG channel starts playing*, not how a trigger reaches the
   digitizer.
2. **EXTTRIG path** (`show_pulse_trig()` only).
   `awg2.free_run_pulse(trigger_out=True)` drives the **physical** AWG2 Trigger
   I/O connector via `AWGqueueMarkerConfig`. This is the wire above. The
   digitizer captures one shot per real edge using EXTTRIG.

## Confirmed

- **`setup_avg_shot()` always configures the digitizer for `EXTTRIG`**
  (`DAQconfig(..., SD_TriggerModes.EXTTRIG)`), regardless of HVI. The digitizer
  side therefore *always* needs a real electrical edge on its TRG IN port — the
  PXI/HVI signal alone never reaches it.
- **The EXTTRIG free-run path works.** `show_pulse_trig()` /
  `test_awg2_triggered_pulses` capture real, overlaid shots with no HVI
  involved. This is the most reliable path we have.
- **`acq_chan` on a data channel clobbers the data.** When an AWG channel has
  both real `DataPulse` data and a marker queued for the same element,
  `Keysight_AWG.add_waveform` *replaces* the analog data with the marker
  waveform (`wave_data = m1`). Under `TESTING_TRIGGER` (`awgs_ch="1,2"`,
  `acq_chan="1m1"`) channel 1 carries both, so its analog output becomes the
  trigger step pulse, not the I-data.
- **`AWGqueueMarkerConfig` can drive the front-panel TRG connector directly**
  (`trgIOmask=1`), independent of any analog channel — the supported, non-
  clobbering way to emit a hardware trigger synced to a waveform.
- **M3601A (the HVI Designer GUI) is currently inoperable.** The `.HVI` binary
  can be loaded and run, but not inspected, edited, or recompiled.

## Speculation (unverified)

- The `.HVI` binary likely does **not** issue `DAQtrigger()` on the digitizer
  branch — it was probably authored assuming the wired EXTTRIG path. So "pure
  HVI, no wire" triggering (digitizer triggered entirely over the backplane via
  SWHVITRIG) is plausible per the SD1 docs but **unconfirmed**, and can't be
  checked while the GUI is down.
- The long-standing "empty buffer on `measure()`" symptom is consistent with
  the HVI never re-firing its gate per `trigger_period`, so the pulse plays once
  at `start_hvi()` and the capture window catches idle. Not proven.

## Design options given the GUI outage

| Option | Trigger source | Needs `.HVI`? | Sync quality | Notes |
|---|---|---|---|---|
| **1. Software (VI) trigger** | `AWGtrigger()` + `DAQtrigger()` from Python | No | ms-scale jitter | Fine for single-shot diagnostics; too slow for per-cycle averaging. |
| **2. Hardware free-run + wire** | `free_run_pulse(trigger_out=True)` → TRG wire, DIG on EXTTRIG | No | ns-level | Proven (`show_pulse_trig`). Most robust while GUI is down. Requires reworking `measure()`. |
| **3. Keep precompiled `.HVI`** | existing SWHVITRIG binary | Yes (as-is) | n/a | Smallest change, but can't fix the per-cycle gating without the GUI. Single-shot only. |

With M3601A down, **option 2** is the durable path: it has working precedent
and zero dependency on the broken Designer GUI.

## Loose ends to fix regardless

- Move `acq_chan` off any channel listed in `awgs_ch`, or drive the trigger via
  `AWGqueueMarkerConfig` instead of `Constant(..., chan=acq_chan)`, so trigger
  markers never overwrite analog data.
- `take_avg_shot()` now uses the polling `_poll_daq_buffer_get` helper (matching
  `take_raw_shot()`), so a single early/empty `DAQbufferGet` no longer fails the
  read.
