################################################################################
# File:     03_train_category.py
# Author:   Michael Rinderle
# Email:    michael.rinderle@tum.de
# Created:  26.05.2021
#
# Description: Script to train LSTM models to predict the illumination category
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

# define path of stored data
DATA_PATH = os.path.join(DATA_DIR, "all_data.h5")

# limits for scaling
LUX_MAX = 2000
LUX_MIN = 0
# width and step size for data windowing
WINDOW_WIDTH_IN_HOURS = 12
STEP_SIZE = 6
FEATURE_WIDTH = int(WINDOW_WIDTH_IN_HOURS * 60 / 5 / STEP_SIZE)
# train test split ratio
RATIO = 0.9
# number of different categories for one-hot-encoding
NUM_CATEGORY = 3
# number of LSTM cells
NUM_CELLS = 32
# batch size and epochs for model training
BATCH_SIZE = 64
EPOCHS = 100


# initialize lists for train and test data
X_train_combined = []
y_train_combined = []
X_test_combined = []
y_test_combined = []

# list available datasets
with h5py.File(DATA_PATH, "r") as infile:
    grps = list(infile.keys())
    print("Available datasets:")
    print(grps, "\n")

# load datasets from hdf5 file
for dataset in grps:
    lux, cat = zf.get_dataset(DATA_PATH, dataset, "lux", "category")
    lux_scaled = zf.scale(lux, LUX_MIN, LUX_MAX)

    X = zf.timeseries_windowing(lux_scaled,
                                feature_width=FEATURE_WIDTH,
                                label_width=0,
                                step_size=STEP_SIZE)

    y = np.full((len(X)), cat, dtype=int)
    y = tf.one_hot(y, NUM_CATEGORY)

    (X_train, y_train), (X_test, y_test) = zf.train_test_split(X, y, RATIO)

    X_train_combined.append(X_train)
    y_train_combined.append(y_train)
    X_test_combined.append(X_test)
    y_test_combined.append(y_test)

# create tensorflow datasets, shuffle and batch data
train = zf.create_tf_dataset(X_train_combined, y_train_combined)
test = zf.create_tf_dataset(X_test_combined, y_test_combined)
train = train.shuffle(10000).batch(BATCH_SIZE, drop_remainder=True)
test = test.batch(BATCH_SIZE, drop_remainder=True)


# model definition
model = tf.keras.models.Sequential()
model.add(LSTM(NUM_CELLS, batch_input_shape=(BATCH_SIZE, FEATURE_WIDTH, 1)))
model.add(Dense(NUM_CATEGORY, activation="softmax"))

model.compile(optimizer="adam",
              loss="categorical_crossentropy",
              metrics=["accuracy"])

# model training
print("Model training")
model.fit(train, epochs=EPOCHS, batch_size=BATCH_SIZE)

# model evaluation
print("Model evaluation")
model.evaluate(test)

# model saving
MODEL_NAME = f"lstm{NUM_CELLS}_{WINDOW_WIDTH_IN_HOURS}h_step{STEP_SIZE}.h5"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

# save tensorflow model weights
model.save(MODEL_PATH)
# add parameters for scaling and windowing
with h5py.File(MODEL_PATH, "a") as file:
    scaling = file.require_group("scaling_params")
    scaling.require_dataset("val_max", shape=(1,), dtype="uint16")
    scaling.require_dataset("val_min", shape=(1,), dtype="uint16")
    windowing = file.require_group("window_params")
    windowing.require_dataset("step_size", shape=(1,), dtype="uint16")
    windowing.require_dataset("feature_width", shape=(1,), dtype="uint16")

    scaling["val_max"][0] = LUX_MAX
    scaling["val_min"][0] = LUX_MIN
    windowing["step_size"][0] = STEP_SIZE
    windowing["feature_width"][0] = FEATURE_WIDTH
