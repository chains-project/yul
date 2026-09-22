#include <stddef.h>
#include <stdint.h>

/* Simple FNV-1a checksum over a byte buffer. */
uint64_t fnv1a_64(const uint8_t *data, size_t len) {
    uint64_t hash = 0xcbf29ce484222325ULL;
    for (size_t i = 0; i < len; i++) {
        hash ^= (uint64_t)data[i];
        hash *= 0x100000001b3ULL;
    }
    return hash;
}
