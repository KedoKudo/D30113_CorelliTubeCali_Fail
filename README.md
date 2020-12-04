<!-- If the issue was raised by a user they should be named here.
**Original reporter:** [username facility]/[nobody]
-->

Problem Description:
====================
Run 124024, tubes bank7/tube4 and bank8/tube3 were not calibrated in spite of seemingly sufficient pixel count and shadow contrast

Steps to Reproduce:
-------------------
Run the following script in the workbench:
```python
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
```

Investigation/Analysis Results:
-------------------------------

> The original defect was reported in https://code.ornl.gov/sns-hfir-scse/diffraction/single-crystal/single-crystal-diffraction/-/issues/135
