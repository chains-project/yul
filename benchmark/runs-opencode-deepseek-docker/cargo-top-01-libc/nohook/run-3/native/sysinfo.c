#define _POSIX_C_SOURCE 200809L

#include "sysinfo.h"

#include <string.h>
#include <sys/utsname.h>
#include <unistd.h>

long systool_page_size(void) {
    return (long)sysconf(_SC_PAGESIZE);
}

long systool_machine(char *buf, size_t len) {
    struct utsname info;
    size_t n;

    if (buf == NULL || len == 0) {
        return -1;
    }
    if (uname(&info) != 0) {
        return -1;
    }

    n = strlen(info.machine);
    if (n >= len) {
        return -1;
    }
    memcpy(buf, info.machine, n + 1);

    return (long)n;
}

long systool_getpid(void) {
    return (long)getpid();
}
