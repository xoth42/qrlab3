import logging
import time

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

from lib.math import fit

mpl.rcParams["legend.fontsize"] = 7

LOGGER = logging.getLogger(__name__)


class AWGCalibrator:
    """Helper for calibrating AWG offsets, delays, and sideband settings."""

    def __init__(self, awg, sa, delay=0.05, channel_amp=0.6, marker=None):
        self.awg = awg
        self.sa = sa
        self.delay = delay
        self.channel_amp = channel_amp
        self.marker = marker

    def _set_and_confirm(self, param, value):
        """Set an AWG parameter and read it back to ensure the write landed."""
        self.awg.set(param, value)
        self.awg.get(param)

    def _sweep(self, values, setter, sampler):
        """Run a 1D sweep and collect the sampled values."""
        samples = []
        for value in values:
            setter(value)
            samples.append(sampler())
        return np.array(samples)

    def find_channel_offset(self, chan, V0, vrange, N=15, plot=True):
        """
        Find (and set) a channel offset using spectrum analyzer sa:
        - V0: center voltage
        - vrange: from -vrange to +vrange around V0
        - N: number of steps
        - Navg: number of averages per step

        Returns:
        - (Vmin, Pmin)
        """
        vs = np.linspace(V0 - vrange, V0 + vrange, N)
        ps = self._sweep(
            vs,
            lambda v: self._set_and_confirm(f"ch{chan}_offset", v),
            self.sa.get_power,
        )
        f = fit.Polynomial(vs, ps, order=2)
        p0 = [np.min(ps), 0, 1]
        p = f.fit(p0)
        LOGGER.info(f"Fit parameters: {p}", )
        center = -p[1] / 2.0 / p[2]

        if plot:
            plt.plot(
                vs,
                ps,
                label=(
                    f"chan{chan}, V {V0:.03f} +- {vrange:.03f}, "
                    f"C = {center:.03f}"
                ),
            )

        imin = np.argmin(ps)
        LOGGER.info(
            f"Minimum power at {chan} = {vs[imin]:.03f}, fit = {center:.03f}", )

        self.awg.set(f"ch{chan}_offset", vs[imin])
        return vs[imin]

    def calibrate_offsets(
        self, F0, chans, vrange=0.4, plot=True, incremental=False, iterations=6
    ):
        """
        Find (and set) optimal offset voltages on a pair of AWG channels
        by taking several voltage sweeps with binary decreasing voltage range.
        vrange: starting voltage range
        """

        self.sa.set_rf_on(True)

        self.sa.set_frequency(F0)
        self.awg.output_zeros(chans)
        if not incremental:
            self.awg.set(f"ch{chans[0]}_amplitude", self.channel_amp)
            self.awg.set(f"ch{chans[1]}_amplitude", self.channel_amp)
            v1, v2 = 0, 0
            time.sleep(0.2)
        else:
            v1 = self.awg.get(f"ch{chans[0]}_offset")
            v2 = self.awg.get(f"ch{chans[1]}_offset")

        if plot:
            plt.figure()

        for i in range(iterations):
            v1 = self.find_channel_offset(chans[0], v1, vrange, plot=plot)
            v2 = self.find_channel_offset(chans[1], v2, vrange, plot=plot)
            vrange /= 2

        if plot:
            plt.legend(loc="best")

        self.sa.set_rf_on(False)

        return v1, v2

    def optimize_delay_time(self, chan, t0, trange, f1, f2, N=21, ax=None):
        ts = np.linspace(t0 - trange, t0 + trange, N)
        rs = []
        rs2 = []
        for t in ts:
            self._set_and_confirm(f"ch{chan}_skew", t)
            p1 = self.sa.get_power_at(f1)
            p2 = self.sa.get_power_at(f2)
            rs.append(p1 - p2)
            rs2.append(p2)

        if ax:
            ax.plot(ts, rs, label=f"T +- {trange:d} ps")
            ax.plot(ts, rs2, label=f"T +- {trange:d} ps [p1]")

        imax = np.argmin(rs2)
        self.awg.set(f"ch{chan}_skew", ts[imax])
        return ts[imax]

    def optimize_phase(
        self, chans, period, phi0, phirange, f1, f2, N=21, ax=None
    ):
        phis = np.linspace(phi0 - phirange, phi0 + phirange, N)
        rs = []
        rs2 = []
        for phi in phis:
            self.awg.sideband_modulate(period, dphi=phi, chans=chans)
            time.sleep(0.2)
            p1 = self.sa.get_power_at(f1)
            p2 = self.sa.get_power_at(f2)
            LOGGER.info(f"Phi {phi:.03f}, p1 = {p1:.03f}, p2 = {p2:.03f}", )
            rs.append(p1 - p2)
            rs2.append(p2)

        if ax:
            ax.plot(phis, rs, label=f"Phi +- {phirange:.03f}")
            ax.plot(phis, rs2, label=f"Phi +- {phirange:.03f} [p1]")

        imax = np.argmin(rs2)
        self.awg.sideband_modulate(period, dphi=phis[imax], chans=chans)
        return phis[imax]

    def optimize_amplitude(self, chan, amp0, amprange, f1, f2, N=21, ax=None):
        amps = np.linspace(amp0 - amprange, amp0 + amprange, N)
        rs = []
        rs2 = []
        for amp in amps:
            self._set_and_confirm(f"ch{chan}_amplitude", amp)
            time.sleep(self.delay)
            p1 = self.sa.get_power_at(f1)
            p2 = self.sa.get_power_at(f2)
            LOGGER.info(f"Amp {amp:.03f}, p1 = {p1:.03f}, p2 = {p2:.03f}", )
            rs.append(p1 - p2)
            rs2.append(p2)

        if ax:
            ax.plot(amps, rs, label=f"Amp +- {amprange:.03f}")
            ax.plot(amps, rs2, label=f"Amp +- {amprange:.03f}")

        imax = np.argmin(rs2)
        self.awg.set(f"ch{chan}_amplitude", amps[imax])
        return amps[imax]

    def calibrate_sideband_skew(
        self, chan, f1, f2, period, chans=(1, 2), plot=True
    ):
        """
        Optimize IQ mixer for single sideband modulation.
        Frequencies around f1 and f2, awg period <period> on channels <chans>
        """

        # The starting point
        self.awg.sideband_modulate(period, dphi=0, chans=chans)
        self.awg.set(f"ch{chans[0]}_skew", 0)
        self.awg.set(f"ch{chans[1]}_skew", 0)
        self.awg.set(f"ch{chans[0]}_amplitude", self.channel_amp)
        self.awg.set(f"ch{chans[1]}_amplitude", self.channel_amp)
        time.sleep(0.5)

        # Find frequencies more accurately
        # f1 = self.sa.find_peak(f1, 5e6, 41, plot=False)
        # f2 = self.sa.find_peak(f2, 5e6, 41, plot=False)
        LOGGER.info(
            f"Sidebands @ f1 = {f1 / 1000000.0:.03f} MHz, f2 = {f2 / 1000000.0:.03f} MHz", )

        # Check whether the requested sideband needs a pi phase shift on the
        # first channel.
        p1_noflip = self.sa.get_power_at(f1)
        p2_noflip = self.sa.get_power_at(f2)
        r_noflip = p1_noflip - p2_noflip
        self.awg.sideband_modulate(period, dphi=np.pi, chans=chans)
        time.sleep(0.5)
        p1_flip = self.sa.get_power_at(f1)
        p2_flip = self.sa.get_power_at(f2)
        r_flip = p1_flip - p2_flip

        if r_noflip > r_flip:
            LOGGER.info("  Pi phase-shift NOT required.")
            self.awg.sideband_modulate(period, flip=False)
        else:
            LOGGER.info("  Pi phase shift required.")

        if plot:
            ax_time = plt.figure().add_subplot(111)
            ax_amp = plt.figure().add_subplot(111)
        else:
            ax_time = None
            ax_amp = None

        # Starting parameters
        t0 = 0
        trange = 4000
        amp0 = self.awg.get(f"ch{chan}_amplitude")
        amprange = 0.25 * amp0

        for i in range(3):
            t0 = self.optimize_delay_time(chan, t0, trange, f1, f2, ax=ax_time)
            amp0 = self.optimize_amplitude(
                chan, amp0, amprange, f1, f2, ax=ax_amp
            )
            LOGGER.info(f"Optimized t = {t0}, amp = {amp0:.03f}", )

            trange /= 2
            amprange /= 2

        if plot:
            ax_time.autoscale(tight=True)
            ax_time.legend(loc="best")
            ax_amp.autoscale(tight=True)
            ax_amp.legend(loc="best")

    def calibrate_sideband_phase(
        self,
        chans,
        f1,
        f2,
        period,
        iterations=4,
        plot=True,
        divide=2.5,
        find_peaks=False,
    ):
        """
        Optimize IQ mixer for single sideband modulation.
        Frequencies around f1 and f2, awg period <period> on channels <chans>.
        Returns tuple <amplitude>, <phase> for the optimal point.
        """

        # The starting point
        self.awg.sideband_modulate(period, dphi=0, chans=chans)
        # self.awg.set_channel_skew(0, chans[0])
        # self.awg.set_channel_skew(0, chans[1])
        self.awg.set(f"ch{chans[0]}_amplitude", self.channel_amp)
        self.awg.set(f"ch{chans[1]}_amplitude", self.channel_amp)
        self.awg.get(f"ch{chans[0]}_amplitude")
        time.sleep(0.5)

        # Find frequencies more accurately
        if find_peaks:
            f1 = self.sa.find_peak(f1, freqrange=500e3, N=21)
            f2 = self.sa.find_peak(f2, freqrange=500e3, N=21)
        LOGGER.info(
            f"Sidebands @ f1 = {f1 / 1000000.0:.03f} MHz, f2 = {f2 / 1000000.0:.03f} MHz", )

        self.sa.set_rf_on(True)

        if plot:
            ax_phase = plt.figure().add_subplot(111)
            ax_amp = plt.figure().add_subplot(111)
        else:
            ax_phase = None
            ax_amp = None

        # Starting parameters
        phi0 = np.pi
        phirange = np.pi
        amp0 = self.awg.get(f"ch{chans[0]}_amplitude")
        amprange = 0.25 * amp0

        # Amplitude and phase seem to be quite independent
        for i in range(iterations):
            phi0 = self.optimize_phase(
                chans, period, phi0, phirange, f1, f2, ax=ax_phase, N=19
            )
            amp0 = self.optimize_amplitude(
                chans[0], amp0, amprange, f1, f2, ax=ax_amp, N=15
            )
            LOGGER.info(f"Optimized phi = {phi0}, amp = {amp0:.03f}", )

            phirange /= divide
            amprange /= divide

        if plot:
            ax_phase.autoscale(tight=True)
            ax_phase.legend(loc="best")
            ax_amp.autoscale(tight=True)
            ax_amp.legend(loc="best")

        self.sa.set_rf_on(False)

        return amp0, phi0

    def get_power_vs_delay(self, chan, t0, trange, f, N=21, ax=None):
        ts = np.linspace(t0 - trange, t0 + trange, N)
        rs = []
        for t in ts:
            self.awg.set(f"ch{chan}_skew", t)
            rs.append(self.sa.get_power_at(f))

        if ax:
            ax.plot(ts, rs, label=f"T +- {int(trange)} ps")

        return np.array(ts), np.array(rs)
