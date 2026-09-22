#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

int32_t native_add(int32_t a, int32_t b) {
    return a + b;
}

pid_t native_getpid(void) {
    return getpid();
}

size_t native_strlen(const char *s) {
    return strlen(s);
}
