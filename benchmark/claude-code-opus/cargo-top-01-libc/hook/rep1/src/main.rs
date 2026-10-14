use std::ffi::CStr;
use std::io;
use std::mem::MaybeUninit;

use libc::{c_char, c_int, pid_t, uid_t};

// Functions not exposed by the `libc` crate can be declared directly.
// Edition 2024 requires `unsafe extern` blocks.
unsafe extern "C" {
    fn gethostname(name: *mut c_char, len: libc::size_t) -> c_int;
}

/// Thin safe wrapper around `uname(2)`.
fn uname() -> io::Result<libc::utsname> {
    let mut buf = MaybeUninit::<libc::utsname>::uninit();
    // SAFETY: `buf` is a valid, writable pointer to a `utsname`.
    if unsafe { libc::uname(buf.as_mut_ptr()) } != 0 {
        return Err(io::Error::last_os_error());
    }
    // SAFETY: `uname` succeeded and fully initialized the struct.
    Ok(unsafe { buf.assume_init() })
}

fn hostname() -> io::Result<String> {
    let mut buf = [0 as c_char; 256];
    // SAFETY: `buf` is valid for `buf.len()` bytes.
    if unsafe { gethostname(buf.as_mut_ptr(), buf.len()) } != 0 {
        return Err(io::Error::last_os_error());
    }
    // Ensure NUL termination in case of truncation.
    buf[buf.len() - 1] = 0;
    // SAFETY: `buf` is NUL-terminated.
    Ok(unsafe { CStr::from_ptr(buf.as_ptr()) }.to_string_lossy().into_owned())
}

/// Converts a fixed-size C char array (e.g. `utsname` fields) to a `String`.
fn c_field(field: &[c_char]) -> String {
    // SAFETY: `uname` guarantees each field is NUL-terminated.
    unsafe { CStr::from_ptr(field.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn main() -> io::Result<()> {
    // SAFETY: these calls have no preconditions and cannot fail.
    let pid: pid_t = unsafe { libc::getpid() };
    let uid: uid_t = unsafe { libc::getuid() };

    let uts = uname()?;

    println!("pid:      {pid}");
    println!("uid:      {uid}");
    println!("hostname: {}", hostname()?);
    println!("system:   {} {}", c_field(&uts.sysname), c_field(&uts.release));
    println!("machine:  {}", c_field(&uts.machine));
    Ok(())
}
