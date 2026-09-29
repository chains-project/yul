#ifndef SYSTOOL_SYSINFO_H
#define SYSTOOL_SYSINFO_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Value of sysconf(_SC_PAGESIZE) in bytes, or -1 on failure. */
long systool_page_size(void);

/* Writes the uname(2) machine name into buf as a NUL-terminated string.
 * Returns the number of bytes written (excluding the NUL), or -1 if the
 * buffer is too small or uname fails. */
long systool_machine(char *buf, size_t len);

/* The calling process id. */
long systool_getpid(void);

#ifdef __cplusplus
}
#endif

#endif /* SYSTOOL_SYSINFO_H */
