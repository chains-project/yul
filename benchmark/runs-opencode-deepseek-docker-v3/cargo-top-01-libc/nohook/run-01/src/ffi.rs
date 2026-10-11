//! Raw bindings to native C functions and OS-level C APIs.
//!
//! Keep every `unsafe` FFI declaration in this module and expose safe Rust
//! wrappers from it. Callers elsewhere in the crate never touch raw pointers.

use libc::{c_char, c_int, c_ulong, pid_t, size_t};

// Functions provided by the bundled C library compiled in `build.rs`.
unsafe extern "C" {
    fn syshelper_sum_bytes(data: *const u8, len: size_t) -> c_ulong;
    fn syshelper_fill(buf: *mut c_char, len: size_t, value: c_char) -> c_int;
}

/// Safe wrapper: sum all bytes in a slice using the native implementation.
pub fn sum_bytes(data: &[u8]) -> u64 {
    // SAFETY: `data.as_ptr()` is valid for `data.len()` bytes for the duration
    // of the call, and the C function only reads that range.
    unsafe { syshelper_sum_bytes(data.as_ptr(), data.len()) as u64 }
}

/// Safe wrapper: fill a byte buffer with `value`, returning bytes written.
pub fn fill(buf: &mut [u8], value: u8) -> i32 {
    // SAFETY: the buffer is valid for `buf.len()` bytes and is only written to.
    unsafe { syshelper_fill(buf.as_mut_ptr() as *mut c_char, buf.len(), value as c_char) }
}

/// OS-level C type (`pid_t`) via the platform `getpid(2)`.
pub fn current_pid() -> pid_t {
    // SAFETY: `getpid` has no preconditions and cannot fail.
    unsafe { libc::getpid() }
}

/// Resolve the host name through `gethostname(2)`, handling `errno` on failure.
pub fn hostname() -> std::io::Result<String> {
    let mut buf = [0 as c_char; 256];

    // SAFETY: `buf` is valid for `buf.len()` bytes.
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len() as size_t) };
    if rc != 0 {
        return Err(std::io::Error::last_os_error());
    }

    // SAFETY: on success the kernel null-terminates the buffer.
    let name = unsafe { std::ffi::CStr::from_ptr(buf.as_ptr()) };
    Ok(name.to_string_lossy().into_owned())
}
