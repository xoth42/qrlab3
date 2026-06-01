import numpy as np


class Interpolator:
    """Simple polynomial interpolator.

    Uses NumPy's `polyfit` to compute polynomial coefficients and evaluates
    the polynomial when called. Coefficients are stored from lowest to
    highest degree so evaluation is straightforward.
    """

    def __init__(self, xs=None, ys=None, order=2):
        if xs is not None:
            self.set_interpolation(xs, ys, order)

    def set_interpolation(self, xs, ys, order=2):
        """Fit a polynomial of given `order` through points (`xs`, `ys`).

        The resulting coefficient array is stored in `self.params` in
        increasing-power order: [c0, c1, c2, ...] so that
        p(x) = c0 + c1*x + c2*x**2 + ...
        """

        xs_arr = np.asarray(xs)
        ys_arr = np.asarray(ys)
        # np.polyfit returns highest-to-lowest degree; reverse for eval
        self.params = np.polyfit(xs_arr, ys_arr, order)[::-1]

    def __call__(self, arg):
        """Evaluate the fitted polynomial at scalar `arg`.

        Uses a simple power accumulation (equivalent to Horner's method but
        kept explicit for clarity): iterate coefficients from c0 upwards
        computing y += c_i * arg**i.
        """

        result = 0.0
        power = 1.0
        for coeff in self.params:
            result += coeff * power
            power *= arg
        return result


class AmpGen:
    """Rotation amplitude generator.

    The `amp_spec` argument configures how rotation amplitudes map to pulse
    amplitudes. Supported formats:

    - single scalar: interpreted as the amplitude for a pi rotation.
    - two-element sequence: (amp_0p5pi, amp_pi) — amplitudes for 0.5*pi and
      pi rotations respectively.
    - sequence with more than two elements: interpreted as pairs
      (angle_in_pi_units, amplitude) ... e.g. (0.25, 0.2, 1.0, 0.5) means
      amplitude 0.2 for 0.25*pi and amplitude 0.5 for 1.0*pi. The angles are
      multiplied by pi internally to obtain radians.
    """

    def __init__(self, amp_spec=None):
        self.interp = Interpolator()
        if amp_spec is not None:
            self.set_amp_spec(amp_spec)

    def set_amp_spec(self, amp_spec):
        """Configure the internal interpolator from `amp_spec`.

        The method normalizes the input into `xs` (angles in radians) and
        `ys` (amplitudes) and fits a polynomial of appropriate order.
        """

        # Distinguish scalar vs sequence inputs in a safe, explicit way.
        try:
            length = len(amp_spec)
        except TypeError:
            amp_spec = [amp_spec]
            length = 1

        if length == 1:
            # Linear interpolation between 0 and pi (1st order)
            self.interp.set_interpolation([0, np.pi], [0, amp_spec[0]], 1)
        elif length == 2:
            # Quadratic interpolation using (0, 0.5*pi, pi)
            self.interp.set_interpolation(
                [0, 0.5 * np.pi, np.pi], [0, amp_spec[0], amp_spec[1]], 2
            )
        else:
            # Treat input as alternating (angle_in_pi_units, amplitude)
            xs = np.array([0] + list(amp_spec[::2])) * np.pi
            ys = np.array([0] + list(amp_spec[1::2]))
            self.interp.set_interpolation(xs, ys, order=len(ys) - 1)

    def __call__(self, arg):
        """Return amplitude for rotation `arg` (radians).

        The sign of `arg` is preserved while the interpolator is evaluated on
        its absolute value so amplitudes are symmetric for ±angles.
        """

        sign = np.sign(arg)
        val = np.abs(arg)
        return sign * self.interp(val)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Example usages / quick visual check
    specs = [
        (0.3, 0.5),
        (0.25, 0.2, 1.0, 0.5),
    ]

    for spec in specs:
        ag = AmpGen(spec)
        xs = np.linspace(-np.pi, np.pi, 41)
        ys = [ag(x) for x in xs]
        plt.plot(xs / np.pi, ys, label=str(spec))

    plt.xlabel('Rotation (pi units)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.show()
