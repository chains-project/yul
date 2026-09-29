//! Raw FFI declarations for the bundled `sysnative` C library.
//!
//! Every function here is `unsafe` to call: pointers are unchecked and error
//! codes are reported through `errno`. Prefer the safe wrappers in
//! [`crate::sys`].

use libc::{c_char, c_int, c_void, size_t};

unsafe extern "C" {
    /// FNV-1a 64-bit hash over `len` bytes at `data`.
    pub fn native_fnv1a(data: *const c_void, len: size_t) -> u64;

    /// Write the process name into `buf`, returning bytes written or -1.
    pub fn native_process_name(buf: *mut c_char, cap: size_t) -> c_int;

    /// Parse a base-10 integer into `out`, returning 0 or -1.
    pub fn native_parse_i64(s: *const c_char, out: *mut i64) -> c_int;

    /// Number of online logical CPUs, or -1 on error.
    pub fn native_cpu_count() -> c_int;
}
