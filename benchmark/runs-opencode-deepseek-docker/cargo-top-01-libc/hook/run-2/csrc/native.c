#define _GNU_SOURCE
#include "native.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

uint64_t native_fnv1a(const void *data, size_t len) {
    const unsigned char *p = (const unsigned char *)data;
    uint64_t hash = 14695981039346656037ULL; /* FNV offset basis */
    size_t i;

    if (p == NULL && len != 0) {
        return 0;
    }

    for (i = 0; i < len; i++) {
        hash ^= (uint64_t)p[i];
        hash *= 1099511628211ULL; /* FNV prime */
    }
    return hash;
}

int native_process_name(char *buf, size_t cap) {
    FILE *f;
    size_t n;

    if (buf == NULL || cap == 0) {
        errno = EINVAL;
        return -1;
    }

    f = fopen("/proc/self/comm", "r");
    if (f == NULL) {
        return -1;
    }

    n = fread(buf, 1, cap - 1, f);
    if (ferror(f)) {
        fclose(f);
        return -1;
    }
    fclose(f);

    if (n > 0 && buf[n - 1] == '\n') {
        n--;
    }
    buf[n] = '\0';
    return (int)n;
}

int native_parse_i64(const char *s, int64_t *out) {
    char *end = NULL;
    long long value;

    if (s == NULL || out == NULL) {
        errno = EINVAL;
        return -1;
    }

    errno = 0;
    value = strtoll(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0') {
        return -1;
    }

    *out = (int64_t)value;
    return 0;
}

int native_cpu_count(void) {
    long n = sysconf(_SC_NPROCESSORS_ONLN);
    if (n < 1) {
        return -1;
    }
    return (int)n;
}
