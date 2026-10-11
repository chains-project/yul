#ifndef SYSTEMS_TOOL_SHIM_H
#define SYSTEMS_TOOL_SHIM_H

#include <stddef.h>
#include <sys/types.h>

#ifdef __cplusplus
extern "C" {
#endif

pid_t shim_getpid(void);
off_t shim_file_size(const char *path);
ssize_t shim_read_prefix(int fd, char *buf, size_t len);

#ifdef __cplusplus
}
#endif

#endif
