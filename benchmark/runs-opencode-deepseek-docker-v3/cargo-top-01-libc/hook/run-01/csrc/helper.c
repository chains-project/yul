#include "helper.h"

#include <unistd.h>

long helper_page_size(void) {
    return sysconf(_SC_PAGESIZE);
}

const char *helper_platform(void) {
#if defined(__linux__)
    return "linux";
#elif defined(__APPLE__)
    return "macos";
#elif defined(_WIN32)
    return "windows";
#else
    return "unknown";
#endif
}

ssize_t helper_write_all(int fd, const void *buf, size_t count) {
    const char *p = buf;
    size_t left = count;

    while (left > 0) {
        ssize_t n = write(fd, p, left);
        if (n < 0) {
            return -1;
        }
        p += n;
        left -= (size_t)n;
    }

    return (ssize_t)count;
}
