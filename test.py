from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from os import path

from corelli.calibration import (apply_calibration, calibrate_banks, day_stamp, load_banks, load_calibration_set,
                                 save_calibration_set, new_corelli_calibration)

# A collection of wire-scans. We use them to populate the database
runs = [(124024, '36-41, 7-10', 'CORELLI_124024_banks_36-41_7-10')]

# Load the integrated count files for all the wire-scans
data_dir = '/SNS/CORELLI/shared/tmp/calibration'  # a temporary calibration

for _, bank_selection, workspace_name in runs:
    file_path = path.join(data_dir, workspace_name + '.nxs')
    load_banks(file_path, bank_selection, output_workspace=workspace_name)

# generating a set of individual bank calibrations
[DeleteWorkspace(name) for name in ['calibrations', 'mask', 'fits'] if AnalysisDataService.doesExist(name) is True]  # first a cleanup
for _, bank_selection, workspace_name in runs:
    calibrate_banks(workspace_name, bank_selection, calibration_group = 'calibrations',
                    mask_group = 'mask', fit_group = 'fits', minimum_intensity=400)


"""
reference
from corelli.calibration.bank import calibrate_banks
from corelli.calibration.utils import apply_calibration, load_banks
counts_file = '/SNS/CORELLI/shared/tmp/CORELLI_124023_counts.nxs'  # counts per pixel already integrated, to save time
load_banks(counts_file, bank_selection='10', output_workspace='counts')
calibrate_banks('counts', bank_selection='10')  # this calculates the calibration for 10 banks
# Now we apply the calibration just to bank10
apply_calibration('counts', 'calib10', output_workspace='counts_10', show_instrument=True)
"""
