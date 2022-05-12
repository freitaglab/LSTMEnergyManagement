################################################################################
# File:     04_predict_category.py
# Author:   Michael Rinderle
# Email:    michael.rinderle@tum.de
# Created:  27.05.2021
#
# Description: Scrit to load LSTM models and analyse prediction accuracy
#
################################################################################


import os
import h5py
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import LSTM, Dense

import zombie_functions as zf


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(THIS_DIR, "../data"))
MODEL_DIR = os.path.abspath(os.path.join(THIS_DIR, "../models"))

# define path of stored data and dataset for predictions
DATA_PATH = os.path.join(DATA_DIR, "all_data.h5")
DATASET = "2020-02-03_90mindark"

# define model to load
MODEL_PATH = os.path.join(MODEL_DIR, "lstm32_12h_step6_v3.h5")


# load parameters for scaling and windowing
with h5py.File(MODEL_PATH, "r") as file:
    scaling = file.get("scaling_params")
    windowing = file.get("window_params")

    LUX_MAX = scaling.get("val_max")[0]
    LUX_MIN = scaling.get("val_min")[0]
    FEATURE_WIDTH = windowing.get("feature_width")[0]
    STEP_SIZE = windowing.get("step_size")[0]

    dense_kernel = file.get("model_weights/dense/dense/kernel:0")[()]
    NUM_CELLS, NUM_CATEGORY = dense_kernel.shape


# load dataset from hdf5 file
lux, cat = zf.get_dataset(DATA_PATH, DATASET, "lux", "category")
lux_scaled = zf.scale(lux, LUX_MIN, LUX_MAX)

X = zf.timeseries_windowing(lux_scaled,
                            feature_width=FEATURE_WIDTH,
                            label_width=0,
                            step_size=STEP_SIZE)

y = np.full((len(X)), cat, dtype=int)
y = tf.one_hot(y, NUM_CATEGORY)


# using a different batch size (1) for predictions is not supported out of the
# box. It is necessary to copy the trained weights into a new model
# https://machinelearningmastery.com/use-different-batch-sizes-training-predicting-python-keras/

model = tf.keras.models.load_model(MODEL_PATH)
weights = model.get_weights()

model = tf.keras.models.Sequential()
model.add(LSTM(NUM_CELLS, batch_input_shape=(1, FEATURE_WIDTH, 1)))
model.add(Dense(NUM_CATEGORY, activation="softmax"))
model.set_weights(weights)


# predict categories
X_data = np.expand_dims(X, axis=2)
prediction = model.predict(X_data, batch_size=1)
prediction = np.argmax(prediction, axis=1)


unique_pred, unique_counts = np.unique(prediction, return_counts=True)
print("Unique categories:", unique_pred)
print("Unique counts:    ", unique_counts)
print("Percentage:       ", unique_counts / len(prediction))
