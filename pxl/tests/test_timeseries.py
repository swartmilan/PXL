from __future__ import division, print_function
from .. import timeseries
from ..timeseries import *
import matplotlib.pyplot as plt
import pandas as pd
import os
from uncertainties import unumpy
from nose.tools import assert_almost_equal


def test_autocorrelation():
    t = np.linspace(0, 1, num=1000)
    fs = 1.0/(t[1] - t[0])
    y = np.sin(2*np.pi*t) #+ 0.5*np.sin(5*t)
    y = np.random.rand(len(t))
    y2 = np.random.rand(len(t))
    tau, rho = autocorr_coeff(y, t, -0.5, 0.5)
    print("Mean autocorrelation coefficient for random time series =",
          rho.mean())
    assert np.abs(rho.max() - 1.0) < 1e-12


def test_spectrum_band_averaging():
    """Test band averaging with `psd` function."""
    from scipy.signal import firwin, lfilter
    n_band_average = 20
    n = 10000
    ts = np.random.randn(n)
    t = np.linspace(0.0, 1.0, num=n)
    N = 5
    Fc = 50
    Fs = 1500
    h = firwin(numtaps=N, cutoff=40, nyq=Fs/2)
    ts = lfilter(h, 1.0, ts) # 'x' is the time-series data you are filtering
    f, spec = timeseries.psd(t, ts, n_band_average=1)
    f2, spec2 = timeseries.psd(t, ts, n_band_average=n_band_average)
    plt.plot(f, spec, label="Raw")
    plt.hold(True)
    plt.plot(f2, spec2, label="Band-averaged over {} bands".format(n_band_average))
    plt.xlabel("$f$")
    plt.ylabel("$S$")
    plt.legend()
    plt.show()


def test_average_over_area():
    x = np.array([-6.0, -2.0, -1.0, 0.0, 1.0, 2.0, 6.0])
    y = np.array([-6.0, -2.0, -1.0, 0.0, 1.0, 2.0, 6.0])
    q = np.ones((x.size, y.size))
    ave = average_over_area(q, x, y)
    print("Computed average is", ave)
    assert np.abs(ave - 1) < 1e-12
    # Now test something a bit harder
    y = np.array([0., 1.])
    q = np.array([[1.0, 0., 0., 0., 0., 0., 1.0],
                  [1.0, 0., 0., 0., 0., 0., 1.0]])
    ave = average_over_area(q, x, y)
    print("Computed average is", ave)
    assert np.abs(ave - 0.33333333333333) < 1e-12


def test_average_over_area_uncertainties():
    """Test `average_over_area` with uncertainties."""
    x = np.array([-6.0, -2.0, -1.0, 0.0, 1.0, 2.0, 6.0])
    y = np.array([0., 1.])
    q = np.array([[1.0, 0., 0., 0., 0., 0., 1.0],
                  [1.0, 0., 0., 0., 0., 0., 1.0]])
    # Convert arrays to have uncertainties
    x = unumpy.uarray(x, 1e-3)
    y = unumpy.uarray(y, 0.6e-2)
    q = unumpy.uarray(q, 1e-2)
    ave = average_over_area(q, x, y)
    print("Computed average is", ave)
    assert np.abs(ave - 0.33333333333333) < 1e-12


def test_integral_scale(plot=False):
    t = np.linspace(0, 1, num=1000)
    u = 0.1*np.random.randn(len(t))
    u += 0.1*np.sin(2*np.pi*t)
    print(integral_scale(u, t, tau2=1.0))
    if plot:
        tau, rho = autocorr_coeff(u, t, 0.0, 0.5)
        plt.figure()
        plt.plot(tau, rho)
        plt.xlabel(r"$\tau$")
        plt.ylabel(r"$\rho$")


def test_runningstd():
    t = np.linspace(0, 10, 10000)
    a = np.sin(2*np.pi*t)
    a += np.random.randn(len(t))
    t_std, a_std = runningstd(t, a, 1000)
    print("Mean of running standard deviation:", a_std.mean())
    print("Standard deviation of test time series:", a.std())
    assert np.abs(a_std.mean() - a.std()) < 0.05
    plt.figure()
    plt.plot(t_std, a_std)
    plt.ylim((-4, 4))
    plt.figure()
    plt.plot(t, a)
    plt.show()


def test_combine_std():
    """Test `timeseries.combine_std`."""
    n = 1e5
    ts = np.random.normal(size=n)
    std_tot = ts.std()
    ts1 = ts[:n/2]
    ts2 = ts[n/2:]
    n1 = len(ts1)
    mean1 = ts1.mean()
    std1 = ts1.std()
    n2 = len(ts2)
    mean2 = ts2.mean()
    std2 = ts2.std()
    assert_almost_equal(ts.mean(), np.mean((mean1, mean2)))
    assert n1 + n2 == n
    n = np.array((n1, n2))
    mean = np.array((mean1, mean2))
    std = np.array((std1, std2))
    assert_almost_equal(std_tot, combine_std(n, mean, std), places=2)
