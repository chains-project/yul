//! Thin safe wrappers around raw libc calls.
//!
//! Keep all `unsafe` FFI here so the rest of the program stays safe Rust.

use std::ffi::CStr;
use std::io;

/// Current process ID.
pub fn getpid() -> libc::pid_t {
    // SAFETY: getpid has no preconditions and cannot fail.
    unsafe { libc::getpid() }
}

/// System hostname via gethostname(2).
pub fn hostname() -> io::Result<String> {
    let mut buf = [0 as libc::c_char; 256];
    // SAFETY: buf is valid for buf.len() bytes.
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    // Guarantee NUL termination in case of truncation.
    buf[buf.len() - 1] = 0;
    // SAFETY: buf is NUL-terminated.
    let s = unsafe { CStr::from_ptr(buf.as_ptr()) };
    Ok(s.to_string_lossy().into_owned())
}

pub struct Uname {
    pub sysname: String,
    pub release: String,
    pub machine: String,
}

/// Kernel identification via uname(2).
pub fn uname() -> io::Result<Uname> {
    // SAFETY: utsname is plain-old-data; all-zero is a valid value.
    let mut uts: libc::utsname = unsafe { std::mem::zeroed() };
    // SAFETY: uts is a valid, writable utsname.
    if unsafe { libc::uname(&mut uts) } != 0 {
        return Err(io::Error::last_os_error());
    }
    let field = |f: &[libc::c_char]| {
        // SAFETY: the kernel NUL-terminates each utsname field.
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pid_is_positive() {
        assert!(getpid() > 0);
    }

    #[test]
    fn hostname_and_uname_work() {
        assert!(!hostname().unwrap().is_empty());
        assert!(!uname().unwrap().sysname.is_empty());
    }
}
