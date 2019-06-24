# -*- coding: utf-8 -*-
"""
Created on Fri Jun 07 18:19:23 2019

@author: wanglab
"""

import numpy as np
import matplotlib.pyplot as plt


def DFT_slow(x):
    """Compute the discrete Fourier Transform of the 1D array x"""
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    n = np.arange(N)
    k = n.reshape((N, 1))
    M = np.exp(-1j * k * n / N)
    return np.dot(M, x)


y = DFT_slow(crosscorr(dT1, dFT1, lags))