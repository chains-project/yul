#ifndef SYS_TOOL_NATIVE_H
#define SYS_TOOL_NATIVE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * FNV-1a 64-bit hash over an arbitrary byte buffer.
 *
 * data: pointer to the first byte (may be NULL only when len == 0)
 * len:  number of bytes to hash
 * Returns the 64-bit digest.
 */
uint64_t native_fnv1a(const void *data, size_t len);

/*
 * Copy the current process name from /proc/self/comm into a caller-owned
 * buffer.
 *
 * buf: destination buffer, always NUL-terminated on success
 * cap: capacity of buf in bytes (must be > 0)
 * Returns the number of bytes written excluding the NUL terminator,
 * or -1 on error with errno set.
 */
int native_process_name(char *buf, size_t cap);

/*
 * Parse a base-10 signed 64-bit integer.
 *
 * s:   NUL-terminated input string
 * out: receives the parsed value on success
 * Returns 0 on success, or -1 on invalid input with errno set.
 */
int native_parse_i64(const char *s, int64_t *out);

/*
 * Number of online logical CPUs.
 *
 * Returns the count (>= 1) on success, or -1 on error with errno set.
 */
int native_cpu_count(void);

#ifdef __cplusplus
}
#endif

#endif /* SYS_TOOL_NATIVE_H */
