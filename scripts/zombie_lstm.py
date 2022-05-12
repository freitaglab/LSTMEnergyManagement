################################################################################
# File:     zombie_lstm.py
# Author:   Michael Rinderle
# Email:    michael.rinderle@tum.de
# Created:  31.05.2021
#
# Description: Custom LSTM cell implementation
#
################################################################################


import numpy as np


class ZombieLSTM:
    def __init__(self, lstm_kernel, lstm_recurrent_kernel, lstm_bias,
                 dense_kernel, dense_bias,
                 val_min, val_max,
                 feature_width, step_size):
        # split kernel matrix
        self.Wi, self.Wf, self.Wc, self.Wo = np.hsplit(lstm_kernel, 4)
        # split recurrent kernel matrix
        self.Ui, self.Uf, self.Uc, self.Uo = np.hsplit(lstm_recurrent_kernel, 4)
        # split bias matrix
        self.bi, self.bf, self.bc, self.bo = np.split(lstm_bias, 4)
        # store dense kernel and bias
        self.Wd = dense_kernel
        self.bd = dense_bias
        # determine number of LSTM units
        self.units = len(self.bi)
        # initialize cell state and hidden state
        self.ct = np.zeros(self.units)
        self.ht = np.zeros(self.units)
        # initialize tanh lookup table
        self.tanh_x = np.linspace(0, 2.5, 26)
        self.tanh_y = np.tanh(self.tanh_x)
        # initialize normalization and feature parameters
        self.val_max = val_max
        self.val_min = val_min
        self.feature_width = feature_width
        self.step_size = step_size

    def export_model(self, filename):
        with open(filename, "w") as file:
            file.write("#ifndef NETWORK_H\n#define NETWORK_H\n\n")

            file.write("const float lstm_wi[{:d}][{:d}] = {{\n{{".format(
                self.Wi.shape[0], self.Wi.shape[1]))
            np.savetxt(file, self.Wi, fmt="%8.5f", delimiter=",", newline="},\n{")
            file.seek(file.tell() - 3)
            file.write("\n};\n\n")

            file.write("const float lstm_wf[{:d}][{:d}] = {{\n{{".format(
                self.Wf.shape[0], self.Wf.shape[1]))
            np.savetxt(file, self.Wf, fmt="%8.5f", delimiter=",", newline="},\n{")
            file.seek(file.tell() - 3)
            file.write("\n};\n\n")

            file.write("const float lstm_wc[{:d}][{:d}] = {{\n{{".format(
                self.Wc.shape[0], self.Wc.shape[1]))
            np.savetxt(file, self.Wc, fmt="%8.5f", delimiter=",", newline="},\n{")
            file.seek(file.tell() - 3)
            file.write("\n};\n\n")

            file.write("const float lstm_wo[{:d}][{:d}] = {{\n{{".format(
                self.Wo.shape[0], self.Wo.shape[1]))
            np.savetxt(file, self.Wo, fmt="%8.5f", delimiter=",", newline="},\n{")
            file.seek(file.tell() - 3)
            file.write("\n};\n\n")

            file.write("const float lstm_ui[{:d}][{:d}] = {{\n{{".format(
                self.Ui.shape[0], self.Ui.shape[1]))
            np.savetxt(file, self.Ui, fmt="%8.5f", delimiter=",", newline="},\n{")
            file.seek(file.tell() - 3)
            file.write("\n};\n\n")

            file.write("const float lstm_uf[{:d}][{:d}] = {{\n{{".format(
                self.Uf.shape[0], self.Uf.shape[1]))
            np.savetxt(file, self.Uf, fmt="%8.5f", delimiter=",", newline="},\n{")
            file.seek(file.tell() - 3)
            file.write("\n};\n\n")

            file.write("const float lstm_uc[{:d}][{:d}] = {{\n{{".format(
                self.Uc.shape[0], self.Uc.shape[1]))
            np.savetxt(file, self.Uc, fmt="%8.5f", delimiter=",", newline="},\n{")
            file.seek(file.tell() - 3)
            file.write("\n};\n\n")

            file.write("const float lstm_uo[{:d}][{:d}] = {{\n{{".format(
                self.Uo.shape[0], self.Uo.shape[1]))
            np.savetxt(file, self.Uo, fmt="%8.5f", delimiter=",", newline="},\n{")
            file.seek(file.tell() - 3)
            file.write("\n};\n\n")

            file.write("const float lstm_bi[{:d}] = {{\n".format(
                self.bi.shape[0]))
            np.savetxt(file, self.bi, fmt="%8.5f", newline=",")
            file.seek(file.tell() - 2)
            file.write("\n};\n\n")

            file.write("const float lstm_bf[{:d}] = {{\n".format(
                self.bf.shape[0]))
            np.savetxt(file, self.bf, fmt="%8.5f", newline=",")
            file.seek(file.tell() - 2)
            file.write("\n};\n\n")

            file.write("const float lstm_bc[{:d}] = {{\n".format(
                self.bc.shape[0]))
            np.savetxt(file, self.bc, fmt="%8.5f", newline=",")
            file.seek(file.tell() - 2)
            file.write("\n};\n\n")

            file.write("const float lstm_bo[{:d}] = {{\n".format(
                self.bo.shape[0]))
            np.savetxt(file, self.bo, fmt="%8.5f", newline=",")
            file.seek(file.tell() - 2)
            file.write("\n};\n\n")

            file.write("const float dense_kernel[{:d}][{:d}] = {{\n{{".format(
                self.Wd.shape[0], self.Wd.shape[1]))
            np.savetxt(file, self.Wd, fmt="%8.5f", delimiter=",", newline="},\n{")
            file.seek(file.tell() - 3)
            file.write("\n};\n\n")

            file.write("const float dense_bias[{:d}] = {{\n".format(
                self.bd.shape[0]))
            np.savetxt(file, self.bd, fmt="%8.5f", newline=",")
            file.seek(file.tell() - 2)
            file.write("\n};\n\n")

            file.write("#define input_size {}\n".format(self.Wi.shape[0]))
            file.write("#define lstm_units {}\n".format(self.units))
            file.write("#define output_size {}\n\n".format(self.Wd.shape[1]))

            file.write("#define val_max {}\n".format(self.val_max))
            file.write("#define val_min {}\n".format(self.val_min))
            file.write("#define step_size {}\n".format(self.step_size))
            file.write("#define feature_width {}\n".format(self.feature_width))

            file.write("\ntypedef struct { float x; float y; } tanh_t;\n\n")
            file.write("tanh_t tanh_lookup[{:d}] = {{\n".format(len(self.tanh_x)))
            for i in range(len(self.tanh_x)):
                file.write("{{{:8.5f}, {:8.5f}}},\n".format(
                    self.tanh_x[i], self.tanh_y[i]))
            file.seek(file.tell() - 2)
            file.write("\n};\n\n")

            file.write("#endif // NETWORK_H")

    def _sigmoid(self, x):
        return (1 + self._tanh(x / 2)) / 2

    def _tanh(self, x):
        # # use exact tanh function
        # return np.tanh(x)

        # use lookup table and linear interpolation
        return np.interp(np.abs(x), self.tanh_x, self.tanh_y, right=1) * np.sign(x)

    def _lstm_step(self, xt):
        # forget gate
        ft = self._sigmoid(np.dot(xt, self.Wf) + np.dot(self.ht, self.Uf) + self.bf)
        # input gate
        it = self._sigmoid(np.dot(xt, self.Wi) + np.dot(self.ht, self.Ui) + self.bi)
        # output gate
        ot = self._sigmoid(np.dot(xt, self.Wo) + np.dot(self.ht, self.Uo) + self.bo)
        # candidate values
        ct = self._tanh(np.dot(xt, self.Wc) + np.dot(self.ht, self.Uc) + self.bc)

        # update cell state and hidden state (pointwise multiplication)
        self.ct = ft * self.ct + it * ct
        self.ht = ot * self._tanh(self.ct)

    def _dense_layer(self):
        return np.dot(self.ht, self.Wd) + self.bd

    def predict(self, x_vector):
        self.ct = np.zeros(self.units)
        self.ht = np.zeros(self.units)
        for x in x_vector:
            self._lstm_step(x)
        return self._dense_layer()

    def contiguous_prediction(self, xt):
        self._lstm_step(xt)
        return self._dense_layer()
