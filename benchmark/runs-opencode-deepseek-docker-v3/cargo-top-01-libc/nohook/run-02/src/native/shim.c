#include "shim.h"

#include <sys/stat.h>
#include <unistd.h>

pid_t shim_getpid(void) {
    return getpid();
}

off_t shim_file_size(const char *path) {
    struct stat st;
    if (stat(path, &st) != 0) {
        return -1;
    }
    return st.st_size;
}

ssize_t shim_read_prefix(int fd, char *buf, size_t len) {
    return read(fd, buf, len);
}
