/* Livermore Loop 7 — equation of state fragment (McMahon 1986, kernel 7).
 * Reference loop, unmodified. 16 FP64 flops per element, n = 995 (LFK long set).
 * Usage: ll7 [min_seconds]   -> prints one JSON line with mflops. */
#include <stdio.h>
#include <stdlib.h>
#include "timer.h"
#include "pcore.h"

#define N 995
static double x[N], u[N + 6], y[N], z[N];

int main(int argc, char **argv) {
    prefer_pcore();
    double min_s = argc > 1 ? atof(argv[1]) : 1.0;
    const double q = 0.5, r = 0.25, t = 0.125;
    for (int k = 0; k < N + 6; k++) u[k] = 1.0 + 1e-3 * k;
    for (int k = 0; k < N; k++) { y[k] = 2.0 + 1e-4 * k; z[k] = 3.0 - 1e-4 * k; x[k] = 0.0; }

    long reps = 1000;
    double elapsed = 0.0, checksum = 0.0;
    for (;;) {
        double t0 = now_s();
        for (long rep = 0; rep < reps; rep++) {
            for (int k = 0; k < N; k++) {
                x[k] = u[k] + r * (z[k] + r * y[k]) +
                       t * (u[k + 3] + r * (u[k + 2] + r * u[k + 1]) +
                            t * (u[k + 6] + q * (u[k + 5] + q * u[k + 4])));
            }
            checksum += x[rep % N];  /* defeat dead-store elimination */
        }
        elapsed = now_s() - t0;
        if (elapsed >= min_s) break;
        reps *= 2;
    }
    double flops = 16.0 * N * (double)reps;
    printf("{\"kernel\":\"ll7\",\"n\":%d,\"reps\":%ld,\"seconds\":%.6f,\"mflops\":%.3f,\"checksum\":%.6e}\n",
           N, reps, elapsed, flops / elapsed / 1e6, checksum);
    return 0;
}
