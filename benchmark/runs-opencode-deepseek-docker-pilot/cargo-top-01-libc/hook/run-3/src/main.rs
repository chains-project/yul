//! A small systems tool that talks to the platform C library.
//!
//! It shows the pieces you need when integrating Rust with native code:
//!
//! * calling C functions through `extern "C"` declarations,
//! * using OS-level C types (`libc::pid_t`, `libc::uid_t`, `libc::utsname`,
//!   `libc::c_char`, ...) directly instead of re-inventing them,
//! * converting between Rust strings and NUL-terminated C strings safely,
//! * turning C error signalling (return `-1` + `errno`) into `std::io::Error`.

use std::ffi::{CStr, CString};
use std::io;
use std::mem::MaybeUninit;

// Functions from the C standard library / libc. The `libc` crate already
// declares most of these; a few are redeclared here to show the raw FFI
// surface. In edition 2024 `extern` blocks must be marked `unsafe`.
unsafe extern "C" {
    fn getpid() -> libc::pid_t;
    fn getuid() -> libc::uid_t;
    fn uname(buf: *mut libc::utsname) -> libc::c_int;
    fn gethostname(name: *mut libc::c_char, len: libc::size_t) -> libc::c_int;
}

// A function from a *separate* native C library (`libm`), wired up by
// `build.rs` via `cargo:rustc-link-lib=m`.
unsafe extern "C" {
    fn cbrt(x: libc::c_double) -> libc::c_double;
}

/// Process identifier, returned as the OS-level `pid_t`.
fn process_id() -> libc::pid_t {
    // SAFETY: `getpid` takes no arguments and cannot fail.
    unsafe { getpid() }
}

/// Real user identifier, returned as the OS-level `uid_t`.
fn user_id() -> libc::uid_t {
    // SAFETY: `getuid` takes no arguments and cannot fail.
    unsafe { getuid() }
}

/// Kernel name/release/machine information via `uname(2)`.
fn system_info() -> io::Result<libc::utsname> {
    let mut buf = MaybeUninit::<libc::utsname>::uninit();

    // SAFETY: `buf` points to enough memory for a `utsname`.
    let rc = unsafe { uname(buf.as_mut_ptr()) };
    if rc == -1 {
        return Err(io::Error::last_os_error());
    }

    // SAFETY: `uname` returned 0, so it initialised the whole struct.
    Ok(unsafe { buf.assume_init() })
}

/// Hostname, exercising a caller-provided C string buffer.
fn hostname() -> io::Result<String> {
    let mut buf = vec![0 as libc::c_char; 256];

    // SAFETY: `buf` is a writable buffer of `buf.len()` bytes.
    let rc = unsafe { gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc == -1 {
        return Err(io::Error::last_os_error());
    }

    // The kernel promises a NUL-terminated result; enforce it defensively
    // before reconstructing a `CStr`.
    if let Some(last) = buf.last_mut() {
        *last = 0;
    }

    // SAFETY: `buf` is NUL-terminated and outlives the borrow.
    let name = unsafe { CStr::from_ptr(buf.as_ptr()) };
    Ok(name.to_string_lossy().into_owned())
}

/// Read an environment variable by handing a Rust-owned `CString` to libc.
fn env_var(name: &str) -> Option<String> {
    let name = CString::new(name).ok()?;

    // SAFETY: `name` is a valid NUL-terminated C string.
    let value = unsafe { libc::getenv(name.as_ptr()) };
    if value.is_null() {
        return None;
    }

    // SAFETY: a non-null `getenv` result is a valid NUL-terminated string
    // owned by the C runtime; we copy out of it immediately.
    Some(
        unsafe { CStr::from_ptr(value) }
            .to_string_lossy()
            .into_owned(),
    )
}

/// Call into libm for the real cube root.
fn cube_root(x: libc::c_double) -> libc::c_double {
    // SAFETY: `cbrt` is a pure function over `f64`.
    unsafe { cbrt(x) }
}

/// Copy a fixed-size, NUL-terminated `c_char` array out of a C struct.
fn c_field(field: &[libc::c_char]) -> String {
    // SAFETY: `uname(2)` always NUL-terminates these fields.
    unsafe { CStr::from_ptr(field.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn main() -> io::Result<()> {
    let info = system_info()?;

    println!("pid:      {}", process_id());
    println!("uid:      {}", user_id());
    println!("hostname: {}", hostname()?);
    println!("sysname:  {}", c_field(&info.sysname));
    println!("release:  {}", c_field(&info.release));
    println!("machine:  {}", c_field(&info.machine));

    match env_var("PATH") {
        Some(path) => println!("PATH:     {path}"),
        None => println!("PATH:     <unset>"),
    }

    println!("cbrt(27): {}", cube_root(27.0));

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cube_root_of_27_is_3() {
        assert!((cube_root(27.0) - 3.0).abs() < f64::EPSILON);
    }

    #[test]
    fn pid_is_positive() {
        assert!(process_id() > 0);
    }

    #[test]
    fn system_info_reports_something() {
        assert!(!c_field(&system_info().unwrap().machine).is_empty());
    }
}
