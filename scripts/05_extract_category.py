################################################################################
# File:     05_extract_category.py
# Author:   Michael Rinderle
# Email:    michael.rinderle@tum.de
# Created:  31.05.2021
#
# Description: Scrit to load LSTM model and export weights to c++ header file
#
################################################################################


import os
import h5py
import numpy as np
import tensorflow as tf

import zombie_functions as zf
from zombie_lstm import ZombieLSTM


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(THIS_DIR, "../data"))
MODEL_DIR = os.path.abspath(os.path.join(THIS_DIR, "../models"))

# define model to load
MODEL_PATH = os.path.join(MODEL_DIR, "lstm32_10h_step6_v1.h5")

# load parameters for scaling and windowing
with h5py.File(MODEL_PATH, "r") as file:
    scaling = file.get("scaling_params")
    windowing = file.get("window_params")

    LUX_MAX = scaling.get("val_max")[0]
    LUX_MIN = scaling.get("val_min")[0]
    FEATURE_WIDTH = windowing.get("feature_width")[0]
    STEP_SIZE = windowing.get("step_size")[0]

# load and initialize custom lstm implementation
with h5py.File(MODEL_PATH, "r") as infile:
    grp = infile.get("model_weights")
    lstm_weights = grp.get("lstm/lstm/lstm_cell")
    dense_weights = grp.get("dense/dense")

    lstm_kernel = lstm_weights.get("kernel:0")[()]
    lstm_bias = lstm_weights.get("bias:0")[()]
    lstm_recurrent_kernel = lstm_weights.get("recurrent_kernel:0")[()]
    dense_kernel = dense_weights.get("kernel:0")[()]
    dense_bias = dense_weights.get("bias:0")[()]

custom_model = ZombieLSTM(lstm_kernel, lstm_recurrent_kernel, lstm_bias,
                          dense_kernel, dense_bias,
                          LUX_MIN, LUX_MAX, FEATURE_WIDTH, STEP_SIZE)

# export custom model into header file
custom_model.export_model("network.h")
