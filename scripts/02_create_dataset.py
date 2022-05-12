################################################################################
# File:     02_create_dataset.py
# Author:   Michael Rinderle
# Email:    michael.rinderle@tum.de
# Created:  18.05.2021
#
# Description: This script converts time-series data stored in separate files
#              and stores them in a single hdf5 file for later use.
#
################################################################################


import h5py
import os
import re
import numpy as np


# define variable length string type for hdf5 attributes
strtype = h5py.special_dtype(vlen=bytes)

# define path of stored data
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(THIS_DIR, "../data"))

# list all hdf5 files in data directory
pattern = re.compile(r"\d{4}-\d{2}-\d{2}_\w+.h5")
hdf5_files = [f for f in os.listdir(DATA_DIR) if pattern.match(f)]
hdf5_files.sort()

# filter files
hdf5_files = hdf5_files

# definition of categories
category_dictionary = {"90mindark": 0, "const": 1, "window": 2}

# find category from filenames
category = np.zeros(len(hdf5_files), dtype=int) - 1
for i, filename in enumerate(hdf5_files):
    for cat_name, cat_id in category_dictionary.items():
        if cat_name in filename:
            category[i] = cat_id


for i, filename in enumerate(hdf5_files):
    # open files to read and write data
    infile = h5py.File(f"{DATA_DIR}/{filename}", "r")
    outfile = h5py.File(f"{DATA_DIR}/all_data.h5", "a")

    # there is only one group in the files
    ingrp = infile.get(list(infile.keys())[0])

    # crete group in output file
    outgrp = outfile.require_group(filename.strip(".h5"))

    # copy the relevant datasets from input to output file
    ingrp.copy("timestamp", outgrp)
    ingrp.copy("voltage", outgrp)
    ingrp.copy("cell_current", outgrp)
    ingrp.copy("lux", outgrp)

    # store the category of the timeseries
    outgrp.require_dataset("category", shape=(1,), dtype="uint8")
    outgrp["category"][0] = category[i]

    # close files
    infile.close()
    outfile.close()
