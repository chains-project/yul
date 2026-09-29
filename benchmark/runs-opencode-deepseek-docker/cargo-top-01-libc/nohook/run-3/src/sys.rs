//! Safe, typed wrappers around the OS primitives used by this tool.
//!
//! Two styles of access are demonstrated:
//!
//! * calls into our own C shim through [`crate::ffi`], and
//! * direct libc calls using the C type aliases from the `libc` crate, whose
//!   size and signedness follow the platform ABI.

use std::ffi::CStr;
use std::io;

use crate::ffi;

/// Buffer size used when reading the machine name from `uname(2)`.
const MACHINE_CAP: usize = 256;

/// The calling process id, obtained through the C shim.
pub fn pid() -> libc::pid_t {
    // `getpid(2)` cannot fail, so the cast is always valid.
    unsafe { ffi::systool_getpid() as libc::pid_t }
}

/// The real user id, read straight from libc using OS-level C types.
pub fn uid() -> libc::uid_t {
    unsafe { libc::getuid() }
}

/// The system page size in bytes, obtained through the C shim.
pub fn page_size() -> io::Result<libc::c_long> {
    let value = unsafe { ffi::systool_page_size() };
    if value < 0 {
        Err(io::Error::last_os_error())
    } else {
        Ok(value)
    }
}

/// The machine hardware name reported by `uname(2)`, obtained through the C
/// shim.
pub fn machine() -> io::Result<String> {
    let mut buf = [0 as libc::c_char; MACHINE_CAP];
    let written = unsafe { ffi::systool_machine(buf.as_mut_ptr(), buf.len()) };

    if written < 0 {
        return Err(io::Error::last_os_error());
    }

    // The shim guarantees a NUL terminator within `buf`.
    let name = unsafe { CStr::from_ptr(buf.as_ptr()) };
    Ok(name.to_string_lossy().into_owned())
}
