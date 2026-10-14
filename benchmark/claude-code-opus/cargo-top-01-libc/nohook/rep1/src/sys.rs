//! Thin safe wrappers around libc. Keep all `unsafe` FFI calls in this module.

use std::ffi::CStr;
use std::io;

use libc::{c_char, gid_t, pid_t, uid_t, utsname};

pub fn getpid() -> pid_t {
    // SAFETY: getpid has no preconditions and cannot fail.
    unsafe { libc::getpid() }
}

pub fn getuid() -> uid_t {
    // SAFETY: getuid has no preconditions and cannot fail.
    unsafe { libc::getuid() }
}

#[allow(dead_code)]
pub fn getgid() -> gid_t {
    // SAFETY: getgid has no preconditions and cannot fail.
    unsafe { libc::getgid() }
}

pub fn hostname() -> io::Result<String> {
    let mut buf = [0 as c_char; 256];
    // SAFETY: buf is valid for buf.len() bytes; we pass len-1 so the result
    // is always NUL-terminated even if the name is truncated.
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len() - 1) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    // SAFETY: buf is NUL-terminated (zero-initialized, last byte never written).
    Ok(unsafe { CStr::from_ptr(buf.as_ptr()) }
        .to_string_lossy()
        .into_owned())
}

pub struct Uname {
    pub sysname: String,
    pub release: String,
    pub machine: String,
}

pub fn uname() -> io::Result<Uname> {
    // SAFETY: utsname is a plain C struct of char arrays; all-zero is valid.
    let mut u: utsname = unsafe { std::mem::zeroed() };
    // SAFETY: &mut u is a valid pointer to a utsname.
    if unsafe { libc::uname(&mut u) } != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(Uname {
        sysname: field(&u.sysname),
        release: field(&u.release),
        machine: field(&u.machine),
    })
}

fn field(chars: &[c_char]) -> String {
    // SAFETY: uname fills each field with a NUL-terminated string.
    unsafe { CStr::from_ptr(chars.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pid_matches_std() {
        assert_eq!(getpid() as u32, std::process::id());
    }

    #[test]
    fn uname_reports_kernel() {
        assert!(!uname().unwrap().sysname.is_empty());
    }
}
