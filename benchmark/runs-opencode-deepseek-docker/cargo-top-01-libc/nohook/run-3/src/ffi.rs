//! Raw `extern "C"` declarations for the shim in `native/sysinfo.c`.
//!
//! `build.rs` compiles that file and links the resulting static library, so
//! no `#[link]` attribute is needed here. The `c_*` aliases from
//! `std::os::raw` are Rust's definitions of the matching C types and are
//! guaranteed to have the correct size and alignment on every target, which
//! is what makes it safe to pass them across the FFI boundary.

use std::os::raw::{c_char, c_long};

extern "C" {
    /// `sysconf(_SC_PAGESIZE)`, or `-1` on failure.
    pub fn systool_page_size() -> c_long;

    /// Copies `uname(2)`'s machine name into `buf` as a NUL-terminated
    /// string. Returns the number of bytes written (excluding the NUL), or
    /// `-1` if `buf` is too small or `uname` fails.
    pub fn systool_machine(buf: *mut c_char, len: usize) -> c_long;

    /// The calling process id.
    pub fn systool_getpid() -> c_long;
}
