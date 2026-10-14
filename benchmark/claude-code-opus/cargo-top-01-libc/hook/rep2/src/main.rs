//! systool: a systems utility that calls native C library functions directly.

use std::ffi::CStr;
use std::io;
use std::mem::MaybeUninit;

/// Returns the current process ID via `getpid(2)`.
fn pid() -> libc::pid_t {
    // SAFETY: getpid has no preconditions and cannot fail.
    unsafe { libc::getpid() }
}

/// Returns kernel/system identification via `uname(2)`.
fn uname() -> io::Result<libc::utsname> {
    let mut buf = MaybeUninit::<libc::utsname>::uninit();
    // SAFETY: buf points to writable memory of the correct size; uname fills it on success.
    if unsafe { libc::uname(buf.as_mut_ptr()) } != 0 {
        return Err(io::Error::last_os_error());
    }
    // SAFETY: uname returned 0, so the struct is fully initialized.
    Ok(unsafe { buf.assume_init() })
}

/// Converts a NUL-terminated `c_char` array from a C struct into a Rust `String`.
fn field(chars: &[libc::c_char]) -> String {
    // SAFETY: utsname fields are NUL-terminated within their fixed-size buffers.
    unsafe { CStr::from_ptr(chars.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn main() -> io::Result<()> {
    let u = uname()?;
    println!("pid:     {}", pid());
    println!("sysname: {}", field(&u.sysname));
    println!("release: {}", field(&u.release));
    println!("machine: {}", field(&u.machine));
    Ok(())
}
