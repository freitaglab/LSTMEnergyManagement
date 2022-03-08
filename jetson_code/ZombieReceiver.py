import netifaces as ni
import selectors
import socket
import struct
import io
import influxdb


# define ip and ports to listen
HOST_IP = "192.168.8.101"
UDP_PORT = 6819
TCP_PORT = 6819

# or get host ip from network interface
HOST_IP = ni.ifaddresses("eth0")[ni.AF_INET][0]["addr"]

# crate InfluxDB client and connect to database
INFLUX_HOST = "localhost"
INFLUX_PORT = 8086
INFLUX_DATABASE = "Zombielab"
influx = influxdb.InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT,
                                 database=INFLUX_DATABASE)


# define name of the current measurement
INFLUX_MEASUREMENT = "test123"

# define size of UDP package and size of single measurements
PACKAGE_SIZE = 1024
MEASUREMENT_SIZE = 32

# define lookup table for IP addresses to sensor names
SENSOR_NAMES = {"192.168.8.111": "Z1",
                "192.168.8.112": "Z2",
                "192.168.8.113": "Z3"}


################################################################################
# helper function to parse the data package and insert them in InfluxDB
def parse_data(data, address):
    # empty list to store InfluxDB insert commands
    influx_points = []

    datastream = io.BytesIO(data)
    for i in range(len(data) // MEASUREMENT_SIZE):
        single_measurement = datastream.read(MEASUREMENT_SIZE)

        # unpack the binary string into separate variables
        # <: little endian
        # f: float | i: int | I: unsigned int | l: long int | s: string
        # number: how many values of the following type
        chunks = struct.unpack("<4f2Ili", single_measurement)

        # construct InfluxDB insert message
        influx_message = {
            "measurement": INFLUX_MEASUREMENT,
            "tags": {"sensor": SENSOR_NAMES[address]},
            "fields": {"voltage": chunks[0],
                       "old_voltage": chunks[1],
                       "cell_current": chunks[2],
                       "lux": chunks[3],
                       "count": chunks[4],
                       "wifi_count": chunks[5],
                       "prediction": chunks[7]},
            # timestamp needs to be in nanosecond precision
            "time": chunks[6]}

        # add InfluxDB insert message to list
        influx_points.append(influx_message)

    # send insert messages to InfluxDB
    print("Write influx points: {}".format(influx_points))
    influx.write_points(influx_points, time_precision="s")  # protocol="json",


################################################################################
# helper function to register udp socket
def register_udp_socket(selector):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.bind((HOST_IP, UDP_PORT))
    udp_sock.setblocking(False)
    print("Listening to UDP packages on {} : {}".format(HOST_IP, UDP_PORT))
    # register udp socket to selector
    selector.register(udp_sock, selectors.EVENT_READ, data=read_udp_package)


# helper function to read udp package
def read_udp_package(selector, socket):
    data, addr = socket.recvfrom(2048)

    print("Got UDP package from {} (IP: {}) | size {}".format(
        SENSOR_NAMES[addr[0]], addr[0], len(data)))

    if len(data) == PACKAGE_SIZE:
        parse_data(data, addr[0])
    else:
        print("ERROR: Received package had wrong size", len(data))


################################################################################
# helper function to register tcp socket
def register_tcp_socket(selector):
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind((HOST_IP, TCP_PORT))
    tcp_sock.setblocking(False)
    tcp_sock.listen(5)
    print("Listening to TCP packages on {} : {}".format(HOST_IP, TCP_PORT))
    # register tcp socket to selector
    selector.register(tcp_sock, selectors.EVENT_READ,
                      data=accept_tcp_connection)


# helper function to accept a tcp connection
def accept_tcp_connection(selector, socket):
    conn, addr = socket.accept()
    conn.setblocking(False)
    # print("Accepted TCP connection from {} (IP: {})".format(
    #     SENSOR_NAMES[addr[0]], addr[0]))
    # register connection socket to selector
    selector.register(conn, selectors.EVENT_READ, data=read_tcp_package)


# helper function to read tcp package
def read_tcp_package(selector, socket):
    data = b""
    addr = socket.getpeername()

    while True:
        try:
            data_part = socket.recv(2048)
            data += data_part
        finally:
            print("Closing TCP connection from {} (IP: {})".format(
                SENSOR_NAMES[addr[0]], addr[0]))
            selector.unregister(socket)
            socket.close()
            break

    print("Got TCP package from {} (IP: {}) | size {}".format(
        SENSOR_NAMES[addr[0]], addr[0], len(data)))

    if (len(data) == PACKAGE_SIZE) or (len(data) == MEASUREMENT_SIZE):
        parse_data(data, addr[0])
    else:
        print("ERROR: Received package had wrong size", len(data))


################################################################################
# main loop to receive data via UDP and insert them in InfluxDB
if __name__ == "__main__":
    # initialize the selector
    sel = selectors.DefaultSelector()

    # register the desired socket
    register_tcp_socket(sel)

    while True:
        # wait for sockets to be ready
        events = sel.select()

        # loop through ready events and call apropriate callback function
        # callback functions are stored in the data property
        for selkey, selmask in events:
            callback = selkey.data
            callback(sel, selkey.fileobj)
