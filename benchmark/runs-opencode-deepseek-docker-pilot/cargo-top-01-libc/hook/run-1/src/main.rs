mod ffi;

use std::ffi::CStr;
use std::io;
use std::os::raw::c_char;

/// Borrow a NUL-terminated C array as an owned Rust `String`.
fn cstr(buf: &[c_char]) -> String {
    unsafe { CStr::from_ptr(buf.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

/// Query the OS hostname through the C `gethostname` API.
fn hostname() -> io::Result<String> {
    let mut buf = [0 as c_char; 256];
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    buf[buf.len() - 1] = 0;
    Ok(cstr(&buf))
}

/// Fill a C `struct utsname` via `uname(2)` and format the interesting fields.
fn uname() -> io::Result<String> {
    let mut uts: libc::utsname = unsafe { std::mem::zeroed() };
    let rc = unsafe { libc::uname(&mut uts) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(format!(
        "{} {} ({})",
        cstr(&uts.sysname),
        cstr(&uts.release),
        cstr(&uts.machine)
    ))
}

fn main() -> io::Result<()> {
    // Direct libc bindings using OS-level C types.
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    println!("pid:       {pid}");
    println!("uid:       {uid}");
    println!("hostname:  {}", hostname()?);
    println!("uname:     {}", uname()?);

    // Native shim: out-parameter written through an OS C type pointer.
    let mut shim_uid: libc::uid_t = 0;
    let rc = unsafe { ffi::shim_get_uid(&mut shim_uid) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    println!("uid(c):    {shim_uid}");
    println!("page size: {}", unsafe { ffi::shim_get_page_size() });

    // C string round-trip: Rust buffer -> native code -> Rust.
    let mut buf = [0 as c_char; 64];
    for (dst, src) in buf.iter_mut().zip(b"systems tool via ffi") {
        *dst = *src as c_char;
    }
    let n = unsafe { ffi::shim_to_uppercase(buf.as_mut_ptr(), buf.len()) };
    println!("upper:     {} ({n} bytes)", cstr(&buf));

    Ok(())
}
