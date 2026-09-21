/* LINPACK benchmark, reference algorithm (Dongarra; C translation after Bonnie Toy 1988).
 * dgefa/dgesl with rolled daxpy/ddot/dscal/idamax — no BLAS substitution, no unrolling.
 * FP64 throughout. MFLOPS = (2/3 n^3 + 2 n^2) / seconds, the LINPACK convention.
 * Usage: linpack <n> [min_seconds]  -> prints one JSON line. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "timer.h"
#include "pcore.h"

static void daxpy(int n, double da, const double *dx, double *dy) {
    if (n <= 0 || da == 0.0) return;
    for (int i = 0; i < n; i++) dy[i] += da * dx[i];
}
static double ddot(int n, const double *dx, const double *dy) {
    double s = 0.0;
    for (int i = 0; i < n; i++) s += dx[i] * dy[i];
    return s;
}
static void dscal(int n, double da, double *dx) {
    for (int i = 0; i < n; i++) dx[i] *= da;
}
static int idamax(int n, const double *dx) {
    int imax = 0; double dmax = fabs(dx[0]);
    for (int i = 1; i < n; i++) if (fabs(dx[i]) > dmax) { dmax = fabs(dx[i]); imax = i; }
    return imax;
}
/* column-major a[lda*n] */
static int dgefa(double *a, int lda, int n, int *ipvt) {
    int info = 0, nm1 = n - 1;
    for (int k = 0; k < nm1; k++) {
        double *col_k = &a[lda * k];
        int l = idamax(n - k, &col_k[k]) + k;
        ipvt[k] = l;
        if (col_k[l] == 0.0) { info = k; continue; }
        if (l != k) { double t = col_k[l]; col_k[l] = col_k[k]; col_k[k] = t; }
        double t = -1.0 / col_k[k];
        dscal(n - k - 1, t, &col_k[k + 1]);
        for (int j = k + 1; j < n; j++) {
            double *col_j = &a[lda * j];
            t = col_j[l];
            if (l != k) { col_j[l] = col_j[k]; col_j[k] = t; }
            daxpy(n - k - 1, t, &col_k[k + 1], &col_j[k + 1]);
        }
    }
    ipvt[n - 1] = n - 1;
    if (a[lda * (n - 1) + (n - 1)] == 0.0) info = n - 1;
    return info;
}
static void dgesl(const double *a, int lda, int n, const int *ipvt, double *b) {
    int nm1 = n - 1;
    for (int k = 0; k < nm1; k++) {
        int l = ipvt[k]; double t = b[l];
        if (l != k) { b[l] = b[k]; b[k] = t; }
        daxpy(n - k - 1, t, &a[lda * k + k + 1], &b[k + 1]);
    }
    for (int kb = 0; kb < n; kb++) {
        int k = n - 1 - kb;
        b[k] /= a[lda * k + k];
        double t = -b[k];
        daxpy(k, t, &a[lda * k], b);
    }
}
static void matgen(double *a, int lda, int n, double *b) {
    long init = 1325;
    for (int j = 0; j < n; j++)
        for (int i = 0; i < n; i++) {
            init = 3125 * init % 65536;
            a[lda * j + i] = (init - 32768.0) / 16384.0;
        }
    for (int i = 0; i < n; i++) b[i] = 0.0;
    for (int j = 0; j < n; j++)
        for (int i = 0; i < n; i++) b[i] += a[lda * j + i];
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: linpack <n> [min_seconds]\n"); return 2; }
    prefer_pcore();
    int n = atoi(argv[1]);
    double min_s = argc > 2 ? atof(argv[2]) : 1.0;
    int lda = n + 1;  /* leading dimension offset, as in the reference */
    double *a = malloc(sizeof(double) * (size_t)lda * n);
    double *b = malloc(sizeof(double) * n);
    double *x = malloc(sizeof(double) * n);
    int *ipvt = malloc(sizeof(int) * n);
    if (!a || !b || !x || !ipvt) return 1;

    long reps = 1; double total = 0.0, resid = 0.0;
    for (;;) {
        total = 0.0;
        for (long rep = 0; rep < reps; rep++) {
            matgen(a, lda, n, b);
            double t0 = now_s();
            dgefa(a, lda, n, ipvt);
            dgesl(a, lda, n, ipvt, b);
            total += now_s() - t0;
        }
        if (total >= min_s) break;
        reps *= 2;
    }
    /* residual check on the last solve: ||A x - b|| with a fresh A */
    for (int i = 0; i < n; i++) x[i] = b[i];
    matgen(a, lda, n, b);
    for (int i = 0; i < n; i++) b[i] = -b[i];
    for (int j = 0; j < n; j++) daxpy(n, x[j], &a[lda * j], b);
    for (int i = 0; i < n; i++) if (fabs(b[i]) > resid) resid = fabs(b[i]);

    double flops_per = 2.0 / 3.0 * (double)n * n * n + 2.0 * (double)n * n;
    double secs = total / reps;
    printf("{\"kernel\":\"linpack%d\",\"n\":%d,\"reps\":%ld,\"seconds\":%.6f,\"mflops\":%.3f,\"resid\":%.3e}\n",
           n, n, reps, secs, flops_per / secs / 1e6, resid);
    return 0;
}
