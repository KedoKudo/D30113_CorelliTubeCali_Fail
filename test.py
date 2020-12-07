from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from os import path

from scipy.ndimage import gaussian_filter

from corelli.calibration import (
    apply_calibration, 
    calibrate_banks, 
    day_stamp, 
    load_banks, 
    load_calibration_set,
    save_calibration_set, 
    new_corelli_calibration,
    )


def clean_signals(signal1D, pixels_per_tube=256, peak_interval_estimate=15):
    _sig_gaussian = gaussian_filter(signal1D, int(peak_interval_estimate/2))
    _sig_tmp = _sig_gaussian - signal1D
    _sig_tmp[_sig_tmp<0] = 1
    _idx = np.where(_sig_tmp==1)[0]
    _sig_tmp[:_idx[0]] = 1
    _sig_tmp[_idx[-1]:] = 1
    #
    _base = np.average(gaussian_filter(signal1D, int(pixels_per_tube/2)))
    return _base - _sig_tmp


runs = [
    (123452, '81-85, 87-90', 'CORELLI_123452_banks_81-85_87_90'),
    (123453, '81-85, 87-90', 'CORELLI_123453_banks_81-85_87_90'),
    (123454, '52-61', 'CORELLI_123454_banks_52-61'),
    (123455, '20-28', 'CORELLI_123455_banks_20-28'),
    (124016, '10-13, 15-19', 'CORELLI_124016_banks_10-13_15-19'),
    (124018, '42-51', 'CORELLI_124018_banks_42-51'),
    (124021, '68-71, 86, 31-35', 'CORELLI_124021_banks_68-71_86_31-35'),
    (124022, '68-71, 86, 31-35', 'CORELLI_124022_banks_68-71_86_31-35'),
    (124023, '10-19', 'CORELLI_124023_banks_10-19'),
    (124024, '36-41, 7-10', 'CORELLI_124024_banks_36-41_7-10'),
    ]

# Macros from utils
n_pixels_per_tube = 256

for n, run in enumerate(runs):
    _, banks, filebase = run
    nxs_file_name = f"/SNS/CORELLI/shared/tmp/calibration/{filebase}.nxs"
    load_banks(nxs_file_name, banks, output_workspace=f"ws_{n}")
    
    # make a clone for calculating the calibration table
    CloneWorkspace(InputWorkspace=f'ws_{n}', OutputWorkspace="_ws")

    _ws = mtd['_ws']
    for i in range(0, _ws.getNumberHistograms(), n_pixels_per_tube):
        _data = np.array([_ws.readY(me) for me in range(i, i+n_pixels_per_tube)])
        _data = clean_signals(_data)
        for j in range(n_pixels_per_tube):
            _ws.setY(i+j, _data[j])
    
    # calculate the calibration table with cleaned signals
    calibrate_banks("_ws", banks)

    # apply the calibration to the original workspace
    apply_calibration(f"ws_{n}", "calibrations", output_workspace=f"ws_{n}_calibrated")

