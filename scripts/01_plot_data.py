################################################################################
# File:     01_plot_data.py
# Author:   Michael Rinderle
# Email:    michael.rinderle@tum.de
# Created:  18.05.2021
# Revision: 23.08.2021 - Add sanity check
#
# Description: Plot recorded timeseries data
#
################################################################################


import h5py
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, MaxNLocator
from matplotlib.dates import DateFormatter

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Palatino"],
})

# define variable length string type for hdf5 attributes
strtype = h5py.special_dtype(vlen=bytes)

# define path of stored data
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(THIS_DIR, "../data"))


def plot_zombie_data(filename, xaxis_relative=False):
    with h5py.File(os.path.join(DATA_DIR, filename), "r") as file:
        # there is only one dataset in the hdf5 files
        dataset = list(file.keys())[0]
        grp = file.get(dataset)
        # get data from hdf5 file
        time = pd.to_datetime(grp.get("timestamp")[()])
        start_time = grp["timestamp"].attrs["start"]
        voltage = np.array(grp.get("voltage")[()])
        cell_current = np.array(grp.get("cell_current")[()])
        lux = np.array(grp.get("lux")[()])
        count = np.array(grp.get("count")[()])
        wifi_count = np.array(grp.get("wifi_count")[()])

    # sanity check (counters increase monotonically)
    check = np.logical_or(np.diff(count) < 0, np.diff(wifi_count) < 0)
    if check.any():  # .
        # filter data in case of any problem
        problem_index = np.argwhere(check).flatten()[0] + 1
        time = time[:problem_index]
        voltage = voltage[:problem_index]
        cell_current = cell_current[:problem_index]
        lux = lux[:problem_index]
        count = count[:problem_index]
        wifi_count = wifi_count[:problem_index]
        print(f"Counters not monotonically increasing in file {filename!r}")
        print(f"The problem occured at index {problem_index} of {len(time)}")

    if xaxis_relative:
        # create x axis relative to first timestep
        timediff = time - time[0]
        xvalues = timediff.astype("timedelta64[m]") / 60
    else:
        xvalues = time
        daymin = xvalues[0].floor("d")
        daymax = xvalues[-1].ceil("d")

    # print timeseries data
    fig = plt.figure(figsize=(8, 5), dpi=160)
    fig.suptitle(os.path.splitext(filename)[0])

    col1 = "tab:blue"
    ax1 = plt.subplot(311)
    ax1.plot(xvalues, voltage, color=col1)
    ax1.tick_params(axis='x', labelbottom=False)
    ax1.set_ylim([2.8, 7])
    ax1.set_yticks([3, 4, 5, 6, 7])
    ax1.set_ylabel("$V_c$ [V]", color=col1)
    ax1.tick_params(axis='y', labelcolor=col1)
    ax1.grid("on")
    # ax1.grid("on", which="major", color="gray", linestyle="-")
    # ax1.grid("on", which="minor", color="lightgray", linestyle='--')

    if xaxis_relative:
        # major ticks every day, minor ticks every 6 hours
        ax1.xaxis.set_major_locator(MultipleLocator(24))
        ax1.xaxis.set_minor_locator(MultipleLocator(6))
        ax1.set_xlim([0, xvalues[-1]])
    else:
        # major ticks every day, minor ticks every 6 hours
        ax1.xaxis.set_major_locator(MultipleLocator(1))
        ax1.xaxis.set_minor_locator(MultipleLocator(0.25))
        # use date formatter for major ticks
        ax1.xaxis.set_major_formatter(DateFormatter(r"%d/%m"))
        ax1.set_xlim([daymin, daymax])

    col21 = "tab:red"
    col22 = "tab:green"
    ax21 = plt.subplot(312, sharex=ax1)
    ax21.plot(xvalues, cell_current, color=col21)
    ax21.tick_params(axis='x', labelbottom=False)
    ax21.set_ylim([0, 1000])
    ax21.yaxis.set_major_locator(MaxNLocator(4))
    ax21.set_ylabel("$I_c$ [µA]", color=col21)
    ax21.tick_params(axis='y', labelcolor=col21)
    ax21.grid("on")
    ax22 = ax21.twinx()
    ax22.plot(xvalues, lux, color=col22)
    ax22.set_ylim([0, max(1200, lux.max())])
    ax22.yaxis.set_major_locator(MaxNLocator(4))
    ax22.set_ylabel("Illum [lux]", color=col22)
    ax22.tick_params(axis='y', labelcolor=col22)

    col31 = "tab:olive"
    col32 = "tab:purple"
    ax31 = plt.subplot(313, sharex=ax1)
    ax31.plot(xvalues, count, color=col31)
    ax31.set_ylim([0, 1.2 * np.ceil(count.max())])
    ax31.yaxis.set_major_locator(MaxNLocator(4))
    ax31.set_ylabel("message count", color=col31)
    ax31.tick_params(axis='y', labelcolor=col31)
    ax31.grid("on")
    ax32 = ax31.twinx()
    ax32.plot(xvalues, wifi_count, color=col32)
    ax32.set_ylim([0, 1.2 * np.ceil(wifi_count.max())])
    ax32.yaxis.set_major_locator(MaxNLocator(4))
    ax32.set_ylabel("wifi count", color=col32)
    ax32.tick_params(axis='y', labelcolor=col32)

    if xaxis_relative:
        ax31.set_xlabel("time [h]")
    else:
        ax31.set_xlabel("date")

    fig.align_ylabels([ax1, ax21, ax31])
    fig.align_ylabels([ax22, ax32])


if __name__ == "__main__":

    # # create a single plot
    # plot_zombie_data("2020-01-14_window.h5", xaxis_relative=True)
    # plt.show()

    # list all hdf5 files in data directory
    pattern = re.compile(r"\d{4}-\d{2}-\d{2}_\w+.h5")
    hdf5_files = [f for f in os.listdir(DATA_DIR) if pattern.match(f)]
    hdf5_files.sort()

    picture_directory = os.path.abspath(os.path.join(THIS_DIR, "../pictures"))
    picture_format = "png"
    for f in hdf5_files:
        plot_zombie_data(f, xaxis_relative=False)
        picture_filename = os.path.splitext(f)[0] + "." + picture_format
        picture_path = os.path.join(picture_directory, picture_filename)
        plt.savefig(picture_path, dpi=192, format=picture_format)
