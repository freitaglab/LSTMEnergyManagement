################################################################################
# File:     zombie_functions.py
# Author:   Michael Rinderle
# Email:    michael.rinderle@tum.de
# Created:  26.05.2021
#
# Description: Helper functions to train and use machine learning models
#              in the smart zombie project
#
################################################################################


import h5py
import numpy as np
import tensorflow as tf


# function to read feature and label data from hdf5 file
def get_dataset(file_path, dataset, feature_key, label_key=None):
    with h5py.File(file_path, "r") as infile:
        features = infile.get(f"/{dataset}/{feature_key}")[()]
        if label_key:
            labels = infile.get(f"/{dataset}/{label_key}")[()]

    if label_key:
        return features, labels
    else:
        return features


# function to create timeseries windows
def timeseries_windowing(data, feature_width=12, label_width=1, step_size=1):

    width = (feature_width + label_width) * step_size

    windows = np.array(
        [data[i:i + width:step_size] for i in range(0, len(data) - width)])

    if label_width:
        X = windows[:, :feature_width]
        y = windows[:, feature_width:]
        return X, y
    else:
        return windows


# function to scale data
def scale(data, min_value, max_value):
    return (data - min_value) / (max_value - min_value)


# function to make a train test split
def train_test_split(X, y, ratio=0.8):
    n_split = int(len(X) * ratio)

    # print("Data length:", len(X))
    # print("Split index:", n_split)

    X_train = X[:n_split]
    y_train = y[:n_split]
    X_test = X[n_split:]
    y_test = y[n_split:]

    return (X_train, y_train), (X_test, y_test)


# function to create tensorflow dataset
def create_tf_dataset(X, y):
    if isinstance(X, list):
        X = np.concatenate(X)
        y = np.concatenate(y)
    if isinstance(X, np.ndarray):
        X = np.expand_dims(X, axis=2)

    # print("X shape:", X.shape)
    # print("y shape:", y.shape)

    return tf.data.Dataset.from_tensor_slices((X, y))
