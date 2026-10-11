#include "device.h"

#include <stddef.h>
#include <sys/stat.h>
#include <unistd.h>

int systool_proc_info_get(systool_proc_info *out) {
    if (out == NULL) {
        return -1;
    }
    out->pid = getpid();
    out->uid = getuid();
    out->gid = getgid();
    out->page_size = sysconf(_SC_PAGESIZE);
    return 0;
}

long systool_page_size(void) {
    return sysconf(_SC_PAGESIZE);
}

int systool_file_dev_ino(const char *path, dev_t *dev, ino_t *ino) {
    struct stat st;
    if (path == NULL || dev == NULL || ino == NULL) {
        return -1;
    }
    if (stat(path, &st) != 0) {
        return -1;
    }
    *dev = st.st_dev;
    *ino = st.st_ino;
    return 0;
}
