#include <stddef.h>
#include <sys/types.h>
#include <unistd.h>

struct example_stats {
    size_t count;
    off_t total;
};

long example_sum(const long *values, size_t len) {
    long total = 0;
    for (size_t i = 0; i < len; i++) {
        total += values[i];
    }
    return total;
}

pid_t example_pid(void) {
    return getpid();
}

void example_collect(const long *values, size_t len, struct example_stats *out) {
    out->count = len;
    out->total = (off_t)example_sum(values, len);
}
