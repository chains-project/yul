#ifndef SYS_TOOL_HELPER_H
#define SYS_TOOL_HELPER_H

#include <stddef.h>
#include <sys/types.h>

long helper_page_size(void);
const char *helper_platform(void);
ssize_t helper_write_all(int fd, const void *buf, size_t count);

#endif
