//! Safe wrappers over the bundled C library and direct libc calls.
//!
//! This module is the only place in the crate that dereferences raw pointers,
//! so the rest of the crate can remain safe Rust.

use crate::ffi;
use libc::{c_char, c_int, c_long, pid_t, uid_t};
use std::ffi::{CStr, CString};
use std::io;

const NAME_CAP: usize = 256;

fn last_errno() -> io::Error {
    io::Error::last_os_error()
}

/// FNV-1a 64-bit hash of `data`.
pub fn fnv1a(data: &[u8]) -> u64 {
    // SAFETY: `data.as_ptr()` is valid for `data.len()` bytes and the C side
    // only reads from it for the duration of the call.
    unsafe { ffi::native_fnv1a(data.as_ptr().cast(), data.len()) }
}

/// Name of the current process, as reported by the kernel.
pub fn process_name() -> io::Result<String> {
    let mut buf = [0 as c_char; NAME_CAP];
    let written = unsafe { ffi::native_process_name(buf.as_mut_ptr(), buf.len()) };
    if written < 0 {
        return Err(last_errno());
    }
    // SAFETY: on success the C side guarantees a NUL terminator in `buf`.
    let cstr = unsafe { CStr::from_ptr(buf.as_ptr()) };
    Ok(cstr.to_string_lossy().into_owned())
}

/// Parse a base-10 signed 64-bit integer, rejecting malformed input.
pub fn parse_i64(s: &str) -> io::Result<i64> {
    let cstr = CString::new(s)
        .map_err(|_| io::Error::new(io::ErrorKind::InvalidInput, "input contains NUL"))?;
    let mut out: i64 = 0;
    let rc = unsafe { ffi::native_parse_i64(cstr.as_ptr(), &mut out) };
    if rc != 0 {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            format!("`{s}` is not a valid base-10 integer"),
        ));
    }
    Ok(out)
}

/// Number of online logical CPUs.
pub fn cpu_count() -> io::Result<c_int> {
    let n = unsafe { ffi::native_cpu_count() };
    if n < 0 {
        return Err(last_errno());
    }
    Ok(n)
}

// --- Direct libc calls using OS-level C types -----------------------------

/// Process ID, using the platform `pid_t` type.
pub fn pid() -> pid_t {
    unsafe { libc::getpid() }
}

/// Real user ID, using the platform `uid_t` type.
pub fn uid() -> uid_t {
    unsafe { libc::getuid() }
}

/// System page size in bytes, as returned by `sysconf` (`c_long`).
pub fn page_size() -> io::Result<c_long> {
    let value = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };
    if value < 0 {
        return Err(last_errno());
    }
    Ok(value)
}

/// Host name via `gethostname(2)`.
pub fn hostname() -> io::Result<String> {
    let mut buf = [0 as c_char; NAME_CAP];
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return Err(last_errno());
    }
    // The kernel NUL-terminates when the name fits; force one in case it was
    // truncated to protect `CStr::from_ptr`.
    buf[NAME_CAP - 1] = 0;
    let cstr = unsafe { CStr::from_ptr(buf.as_ptr()) };
    Ok(cstr.to_string_lossy().into_owned())
}
