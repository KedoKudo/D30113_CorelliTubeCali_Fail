from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from os import path

from scipy.signal import gaussian_filter1d

from corelli.calibration import (
    apply_calibration, 
    calibrate_banks, 
    day_stamp, 
    load_banks, 
    load_calibration_set,
    save_calibration_set, 
    new_corelli_calibration,
    )

# isolate bank 7 and bank 8
nxs_file_name = "/SNS/CORELLI/shared/tmp/calibration/CORELLI_124024_banks_36-41_7-10.nxs"
load_banks(nxs_file_name, "36-41, 7-10", output_workspace="ws")

# clone the workspace
CloneWorkspace(InputWorkspace='ws', OutputWorkspace="ws_cleaned")


def clean_signals(signal1D, pixels_per_tube=256, peak_interval_estimate=15):
    _sig_gaussian = gaussian_filter1d(signal1D, int(peak_interval_estimate/2))
    _sig_tmp = _sig_gaussian - signal1D
    _sig_tmp[_sig_tmp<0] = 1
    _idx = np.where(_sig_tmp==1)[0]
    _sig_tmp[:_idx[0]] = 1
    _sig_tmp[_idx[-1]:] = 1
    #
    _base = np.average(gaussian_filter1d(signal1D, int(pixels_per_tube/2)))
    return _base - _sig_tmp

ws = mtd['ws']
ws_cleaned = mtd['ws_cleaned']
n_pixels_per_tube = 256

# go over one tube at a time (can parallel if needed)
for i in range(0, ws.getNumberHistograms(), n_pixels_per_tube):
    _data = np.array([ws.readY(me) for me in range(i, i+n_pixels_per_tube)])
    _data = clean_signals(_data)
    _ = [ws_cleaned.setY(me, _data[me]) for me in range(i, i+n_pixels_per_tube)]

# calculate the calibration using cleaned data
calibrate_banks("ws_cleaned", "36-41, 7-10")

# apply the calibration to original data
apply_calibration("ws", "calibrations", output_workspace="ws_calibrated", show_instrument=True)
