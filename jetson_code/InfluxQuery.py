import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import h5py
import influxdb


# crate InfluxDB client and connect to database
INFLUX_HOST = "localhost"
INFLUX_PORT = 8086
INFLUX_DATABASE = "Zombielab"
influx = influxdb.InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DATABASE)


# define measurement to query data from
INFLUX_MEASUREMENT = "test123"

# define query command
# SELECT <fields, tags> FROM <measurement> WHERE <filters>
# <fields, tags>: comma separated list of fields and/or tags to query
#                 (a * means all available fields and keys)
# <measurement>:  name of the measurement to query data from
# <filters>:      filter results based on tags (or fields or timestamps)
#                 single quotes around strings are important!
#
# example queries
# "SELECT * FROM {}".format(INFLUX_MEASUREMENT)
# "SELECT voltage,cell_current,lux FROM {} WHERE sensor='Z1'".format(INFLUX_MEASUREMENT)
# "SELECT * FROM {} WHERE sensor='Z1' AND voltage > 3.0 AND time > '2019-09-23T16:00:00Z'".format(INFLUX_MEASUREMENT)

INFLUX_QUERY = "SELECT * FROM {}".format(INFLUX_MEASUREMENT)


# define output filenames (or paths)
# empty string means file will not be saved
# multiple measurements in single hdf5 file are possible!
CSV_FILENAME = "test.csv"
H5_FILENAME = "test.h5"


################################################################################
# main loop to query InfluxDB data and save csv and hdf5 files
if __name__ == "__main__":
    # Query data from InfluxDB
    result = influx.query(INFLUX_QUERY, database=INFLUX_DATABASE)
    # convert results into pandas table
    table = pd.DataFrame(result.get_points())

    # save table to csv file
    if CSV_FILENAME != "":
        table.to_csv(CSV_FILENAME, index=False)

    # save table to hdf5 file
    if H5_FILENAME != "":
        start = table["time"][0]
        # translate time to timestamp for more efficient storage
        table["timestamp"] = pd.to_datetime(table["time"]).astype(int)
        table.drop("time", axis=1, inplace=True)

        with h5py.File(H5_FILENAME, "a") as file:
            # create group to store data (named like measurement)
            grp = file.require_group(INFLUX_MEASUREMENT)

            # loop through table columns and store data
            for key, values in table.iteritems():
                if (key == "timestamp"):
                    # save timestamp as int64
                    thistype = "int64"
                elif (type(values[0]) == np.int64):
                    # save other integer types as int32
                    thistype = "int32"
                elif (type(values[0]) == np.float64):
                    # save float values as float32
                    thistype = "float32"
                elif (type(values[0]) == str):
                    # save string values (tags) as enumerated type
                    tagvals = set(values)
                    tagdict = dict(zip(tagvals, range(len(tagvals))))
                    thistype = h5py.special_dtype(enum=("uint8", tagdict))
                    # transform valuees into enumerated type
                    values = np.vectorize(tagdict.get)(values)

                # create dataset and store values
                dset = grp.require_dataset(key, shape=values.shape, dtype=thistype)
                dset[()] = values

            # add additional notes to file
            strtype = h5py.special_dtype(vlen=bytes)
            grp["timestamp"].attrs.create("start", start, dtype=strtype)

    # plot data
    table["time"] = pd.to_datetime(table["timestamp"])
    table.drop("timestamp", axis=1, inplace=True)
    table.set_index("time", inplace=True)
    table.plot(subplots=True)
    plt.show()
