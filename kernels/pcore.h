#ifndef PCORE_H
#define PCORE_H
/* macOS has no CPU affinity API. QOS_CLASS_USER_INTERACTIVE is the strongest
 * available hint that this thread belongs on a performance core; without it the
 * scheduler may place a benchmark on an efficiency core (observed: 3x spread). */
#ifdef __APPLE__
#include <pthread.h>
#include <sys/qos.h>
static void prefer_pcore(void) { pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0); }
#else
static void prefer_pcore(void) {}
#endif
#endif
