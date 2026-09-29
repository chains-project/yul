#ifndef SYSFFI_SHIM_H
#define SYSFFI_SHIM_H

#include <stddef.h>
#include <sys/types.h>

long shim_get_page_size(void);
int shim_get_uid(uid_t *out);
size_t shim_to_uppercase(char *buf, size_t len);

#endif
