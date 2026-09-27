//! Safe wrappers around native C library calls and OS-level C types.

use std::ffi::CStr;
use std::io;
use std::os::raw::c_char;

use libc::{c_int, c_long, gid_t, pid_t, uid_t};

const HOSTNAME_MAX: usize = 256;

extern "C" {
    fn gethostname(name: *mut c_char, len: usize) -> c_int;
    fn getpid() -> pid_t;
    fn getppid() -> pid_t;
    fn getuid() -> uid_t;
    fn getgid() -> gid_t;
    fn sysconf(name: c_int) -> c_long;
    fn getloadavg(loadavg: *mut f64, nelem: c_int) -> c_int;
}

pub fn pid() -> pid_t {
    unsafe { getpid() }
}

pub fn parent_pid() -> pid_t {
    unsafe { getppid() }
}

pub fn uid() -> uid_t {
    unsafe { getuid() }
}

pub fn gid() -> gid_t {
    unsafe { getgid() }
}

pub fn hostname() -> io::Result<String> {
    let mut buf: [c_char; HOSTNAME_MAX] = [0; HOSTNAME_MAX];
    let rc = unsafe { gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    let name = unsafe { CStr::from_ptr(buf.as_ptr()) };
    Ok(name.to_string_lossy().into_owned())
}

pub fn cpu_count() -> io::Result<usize> {
    let rc = unsafe { sysconf(libc::_SC_NPROCESSORS_ONLN) };
    if rc < 1 {
        return Err(io::Error::last_os_error());
    }
    Ok(rc as usize)
}

pub fn load_average() -> io::Result<[f64; 3]> {
    let mut avg = [0.0_f64; 3];
    let rc = unsafe { getloadavg(avg.as_mut_ptr(), avg.len() as c_int) };
    if rc != avg.len() as c_int {
        return Err(io::Error::last_os_error());
    }
    Ok(avg)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pid_is_positive() {
        assert!(pid() > 0);
    }

    #[test]
    fn hostname_is_not_empty() {
        assert!(!hostname().unwrap().is_empty());
    }

    #[test]
    fn cpu_count_is_positive() {
        assert!(cpu_count().unwrap() >= 1);
    }
}
