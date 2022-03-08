#include "network_category_v3.h"


// initialize lstm cell state and hidden state
RTC_DATA_ATTR float lstm_ct[lstm_units] = {0};
RTC_DATA_ATTR float lstm_ht[lstm_units] = {0};
// initialize persistent memory for lstm input
RTC_DATA_ATTR float lstm_input[feature_width * step_size] = {0};
// initialize lstm prediction
RTC_DATA_ATTR int lstm_output = 0;

const int tanh_lookup_len  = sizeof(tanh_lookup) / sizeof(tanh_lookup[0]);
const int lstm_input_width = feature_width * step_size;


/**
 * Reset cell state and hidden state to 0-vector
 */
void lstm_reset_state() {
    for (int i = 0; i < lstm_units; ++i) {
        lstm_ct[i] = 0;
        lstm_ht[i] = 0;
    }
}


/**
 * Get tanh from lookup table and interpolate between values
 */
float lstm_tanh_interp(float x) {
    int   sgn_x = (x >= 0) - (x < 0);
    float abs_x = sgn_x * x;
    float tanh  = 0;

    if (abs_x > tanh_lookup[tanh_lookup_len - 1].x) {
        return sgn_x;
    }

    for (int i = 0; i < tanh_lookup_len - 1; ++i) {
        if (abs_x >= tanh_lookup[i].x && abs_x < tanh_lookup[i + 1].x) {
            float dx = tanh_lookup[i + 1].x - tanh_lookup[i].x;
            float dy = tanh_lookup[i + 1].y - tanh_lookup[i].y;

            tanh = tanh_lookup[i].y + dy * (abs_x - tanh_lookup[i].x) / dx;
            break;
        }
    }

    return tanh * sgn_x;
}


/**
 * Get sigmoid
 */
float lstm_sigmoid_interp(float x) {
    return (1 + lstm_tanh_interp(x / 2)) / 2;
}


/**
 * Compute one step of the LSTM cells
 */
void lstm_step(float input) {
    float ft[lstm_units] = {0};
    float it[lstm_units] = {0};
    float ot[lstm_units] = {0};
    float ct[lstm_units] = {0};

    for (int i = 0; i < lstm_units; ++i) {
        ft[i] = input * lstm_wf[0][i] + lstm_bf[i];
        it[i] = input * lstm_wi[0][i] + lstm_bi[i];
        ot[i] = input * lstm_wo[0][i] + lstm_bo[i];
        ct[i] = input * lstm_wc[0][i] + lstm_bc[i];
        for (int j = 0; j < lstm_units; ++j) {
            ft[i] += lstm_ht[j] * lstm_uf[j][i];
            it[i] += lstm_ht[j] * lstm_ui[j][i];
            ot[i] += lstm_ht[j] * lstm_uo[j][i];
            ct[i] += lstm_ht[j] * lstm_uc[j][i];
        }
        ft[i] = lstm_sigmoid_interp(ft[i]);
        it[i] = lstm_sigmoid_interp(it[i]);
        ot[i] = lstm_sigmoid_interp(ot[i]);
        ct[i] = lstm_tanh_interp(ct[i]);
    }
    for (int i = 0; i < lstm_units; ++i) {
        lstm_ct[i] = ft[i] * lstm_ct[i] + it[i] * ct[i];
        lstm_ht[i] = ot[i] * lstm_tanh_interp(lstm_ct[i]);
    }
}


/**
 * Compute one step of the dense layer after the LSTM cells and store the
 * predicted category in the `lstm_output` variable
 */
void lstm_dense_layer() {
    float dense_res[output_size] = {0};
    for (int j = 0; j < output_size; ++j) {
        dense_res[j] = dense_bias[j];
        for (int i = 0; i < lstm_units; ++i) {
            dense_res[j] += dense_kernel[i][j] * lstm_ht[i];
        }
    }

    // find category and store it in lstm_output
    float max_val = 0;
    for (int j = 0; j < output_size; ++j) {
        if (max_val < dense_res[j]) {
            max_val = dense_res[j];

            lstm_output = j;
        }
    }
}


/**
 * Scaling of input to ensure values between zero and one
 */
float lstm_scale_input(float input) {
    return (input - val_min) / (val_max - val_min);
}


/**
 * Run the LSTM prediction for the given input value
 * The predicted category is stored in the `lstm_output` variable
 */
void lstm_prediction(float input) {
    // store current lstm input in persistent input vector
    int current_position         = (measure_ctr - 1) % lstm_input_width;
    lstm_input[current_position] = lstm_scale_input(input);

    // return if measure counter is smaller than required lstm window size
    if ((measure_ctr - 1) < lstm_input_width) {
        lstm_output = -1;
        return;
    }

    // reset lstm state
    lstm_reset_state();

    // take the last n time steps and feed them into the lstm network
    int loop_start = (current_position + step_size) % lstm_input_width;
    for (int i = 0; i < lstm_input_width; i += step_size) {
        lstm_step(lstm_input[(loop_start + i) % lstm_input_width]);
        lstm_dense_layer();
    }

#if SERIAL_MONITOR
    Serial.printf("\nLSTM Prediction: %d\n", lstm_output);
#endif
}
