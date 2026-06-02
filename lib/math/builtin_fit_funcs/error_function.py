import numpy as np
import scipy.special as special

# The fitting function, should have "xs" as first parameter.
# Each further parameter is interpreted as a fitting parameters. A default
# value should be specified if no "guess" function is provided
def func(xs, A=1, b=10, x0=10, ofs=0):
    return A * special.erf(b * (xs - x0)) + ofs

# The guess function should produce a dictionary of parameter values that are
# a decent starting point for fitting.
def guess(xs, ys):
    yofs = np.average(ys)
    return dict(
        A = np.max(ys) - np.min(ys),
        b = 10,
        x0 = guess_x0(xs, ys),
        ofs = yofs,
    )

def guess_x0(xs, ys):
    # The steepest slope is a good first guess for the center position.
    derivs = np.array([ys[i + 1] - ys[i] for i in range(len(ys) - 1)])
    return xs[np.argmax(np.abs(derivs))]
