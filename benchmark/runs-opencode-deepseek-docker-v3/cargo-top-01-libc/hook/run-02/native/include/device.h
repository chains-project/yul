#ifndef SYSTOOL_DEVICE_H
#define SYSTOOL_DEVICE_H

#include <sys/types.h>

typedef struct {
    pid_t pid;
    uid_t uid;
    gid_t gid;
    long page_size;
} systool_proc_info;

int systool_proc_info_get(systool_proc_info *out);

long systool_page_size(void);

int systool_file_dev_ino(const char *path, dev_t *dev, ino_t *ino);

#endif
