#include "shim.h"

#include <ctype.h>
#include <unistd.h>

long shim_get_page_size(void) {
    return sysconf(_SC_PAGESIZE);
}

int shim_get_uid(uid_t *out) {
    if (out == NULL) {
        return -1;
    }
    *out = getuid();
    return 0;
}

size_t shim_to_uppercase(char *buf, size_t len) {
    size_t n = 0;
    while (n < len && buf[n] != '\0') {
        buf[n] = (char)toupper((unsigned char)buf[n]);
        n++;
    }
    return n;
}
