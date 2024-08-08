from __future__ import annotations
from dataclasses import dataclass
from flightanalysis.base.ref_funcs import RFuncBuilders
import numpy.typing as npt
import numpy as np
from scipy.signal import filtfilt
from scipy.signal import butter


smoothers = RFuncBuilders({})


def _convolve(data: npt.NDArray, width: float):
    kernel = np.ones(width) / width
    outd = np.full(len(data), np.nan)
    conv = np.convolve(data, kernel, mode="valid")
    ld = (len(data) - len(conv)) / 2
    ldc = int(np.ceil(ld))
    ldf = int(np.floor(ld))
    outd[ldf:-ldc] = conv
    outd[:ldf] = np.linspace(np.mean(data[:ldf]), conv[0], ldf + 1)[:-1]
    outd[-ldc:] = np.linspace(conv[-1], np.mean(data[-ldc:]), ldc + 1)[1:]
    return outd


@smoothers.add
def none(data):
    return data


@smoothers.add
def convolve(data, window_ratio, max_window):
    window = min(len(data) // window_ratio, max_window)
    sample = _convolve(data, window)
    _mean = np.mean(sample)
    sample = (sample - _mean) * window / max_window + _mean
    return sample


@smoothers.add
def lowpass(data, cutoff, order):
    return filtfilt(
        *butter(order, cutoff, fs=25, btype="low", analog=False),
        data,
        padlen=len(data) - 1,
    )

def _soft_end(data, width):
    outd = data.copy()
    width = int(min(np.ceil(len(data) / 4), width))
    outd[-width:] = np.linspace(data[-width], np.mean(data[-width:]), width+1)[1:]
    return outd


@smoothers.add
def soft_end(data, width):
    return _soft_end(data, width)


def _soft_start(data, width):
    outd = data.copy()
    width = int(min(np.ceil(len(data) / 4), width))
    outd[:width] = np.linspace(np.mean(data[:width]), data[width], width+1)[:-1]
    return outd


@smoothers.add
def soft_start(data, width):
    return _soft_start(data, width)    

@smoothers.add
def soft_ends(data, width):
    return _soft_start(_soft_end(data, width), width)