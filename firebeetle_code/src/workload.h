#ifndef WORKLOAD_H
#define WORKLOAD_H


#define MAT_SIZE_I 32
#define MAT_SIZE_J 128
#define MAT_SIZE_K 64


// matrix initialization
float matrix_A[MAT_SIZE_I][MAT_SIZE_J] = {0};
float matrix_B[MAT_SIZE_J][MAT_SIZE_K] = {0};
float matrix_C[MAT_SIZE_I][MAT_SIZE_K] = {0};


void workload(int iterations) {
    // put in some numbers into the matrices
    for (int i = 0; i < MAT_SIZE_I; ++i) {
        for (int j = 0; j < MAT_SIZE_J; ++j) {
            matrix_A[i][j] = i + (2 * j);
        }
    }
    for (int j = 0; j < MAT_SIZE_J; ++j) {
        for (int k = 0; k < MAT_SIZE_K; ++k) {
            matrix_B[j][k] = (3 * k) - j;
        }
    }

    // run the matrix multiplication
    for (int iter = 0; iter < iterations; ++iter) {
        for (int subiter = 0; subiter < 10; ++subiter) {
            for (int i = 0; i < MAT_SIZE_I; ++i) {
                for (int k = 0; k < MAT_SIZE_K; ++k) {
                    matrix_C[i][k] = 0;
                    for (int j = 0; j < MAT_SIZE_J; ++j) {
                        matrix_C[i][k] += matrix_A[i][j] * matrix_B[j][k];
                    }
                }
            }
        }
    }
}


#endif    // WORKLOAD_H
