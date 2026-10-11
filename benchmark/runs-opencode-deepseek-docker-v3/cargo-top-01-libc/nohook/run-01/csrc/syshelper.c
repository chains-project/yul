#include <stddef.h>

unsigned long syshelper_sum_bytes(const unsigned char *data, size_t len) {
    unsigned long total = 0;
    for (size_t i = 0; i < len; i++) {
        total += data[i];
    }
    return total;
}

int syshelper_fill(char *buf, size_t len, char value) {
    if (buf == NULL || len == 0) {
        return -1;
    }
    for (size_t i = 0; i < len; i++) {
        buf[i] = value;
    }
    return (int)len;
}
