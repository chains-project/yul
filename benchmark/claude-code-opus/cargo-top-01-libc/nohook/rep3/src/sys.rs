//! Thin, safe wrappers over native C APIs.
//!
//! All `unsafe` FFI lives in this module so the rest of the crate can stay safe.

use std::ffi::{CStr, CString};
use std::io;
use std::mem::MaybeUninit;

use libc::{c_char, c_int, pid_t, size_t, uid_t};

// Declarations for C functions not covered by the `libc` crate go here.
// Edition 2024 requires extern blocks to be marked `unsafe`.
unsafe extern "C" {
    fn gethostname(name: *mut c_char, len: size_t) -> c_int;
}

/// Converts a C-style `-1` return into the current `errno` as an `io::Error`.
fn cvt(ret: c_int) -> io::Result<c_int> {
    if ret == -1 {
        Err(io::Error::last_os_error())
    } else {
        Ok(ret)
    }
}

pub fn pid() -> pid_t {
    // SAFETY: getpid has no preconditions and cannot fail.
    unsafe { libc::getpid() }
}

pub fn uid() -> uid_t {
    // SAFETY: getuid has no preconditions and cannot fail.
    unsafe { libc::getuid() }
}

pub fn hostname() -> io::Result<String> {
    let mut buf = [0 as c_char; 256];
    // SAFETY: buf is valid for writes of buf.len() bytes.
    cvt(unsafe { gethostname(buf.as_mut_ptr(), buf.len()) })?;
    // gethostname may not NUL-terminate on truncation; force it.
    buf[buf.len() - 1] = 0;
    // SAFETY: buf is NUL-terminated and outlives the borrow.
    let name = unsafe { CStr::from_ptr(buf.as_ptr()) };
    Ok(name.to_string_lossy().into_owned())
}

pub struct Uname {
    pub sysname: String,
    pub release: String,
    pub machine: String,
}

pub fn uname() -> io::Result<Uname> {
    let mut uts = MaybeUninit::<libc::utsname>::uninit();
    // SAFETY: uts points to writable storage for a utsname.
    cvt(unsafe { libc::uname(uts.as_mut_ptr()) })?;
    // SAFETY: uname succeeded, so uts is fully initialized.
    let uts = unsafe { uts.assume_init() };
    let field = |f: &[c_char]| {
        // SAFETY: uname fills each field with a NUL-terminated string.
        unsafe { CStr::from_ptr(f.as_ptr()) }
            .to_string_lossy()
            .into_owned()
    };
    Ok(Uname {
        sysname: field(&uts.sysname),
        release: field(&uts.release),
        machine: field(&uts.machine),
    })
}

/// Returns `(total_bytes, available_bytes)` for the filesystem containing `path`.
// statvfs field widths vary by target (u32 on 32-bit), so the conversions are not always no-ops.
#[allow(clippy::useless_conversion)]
pub fn fs_space(path: &str) -> io::Result<(u64, u64)> {
    let c_path = CString::new(path).map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e))?;
    let mut st = MaybeUninit::<libc::statvfs>::uninit();
    // SAFETY: c_path is a valid C string; st points to writable storage.
    cvt(unsafe { libc::statvfs(c_path.as_ptr(), st.as_mut_ptr()) })?;
    // SAFETY: statvfs succeeded, so st is fully initialized.
    let st = unsafe { st.assume_init() };
    let frsize = u64::from(st.f_frsize);
    Ok((
        u64::from(st.f_blocks) * frsize,
        u64::from(st.f_bavail) * frsize,
    ))
}
