use std::ffi::CStr;
use std::io;

/// Reads the current process ID and hostname straight from libc, showing how
/// to call native C functions and work with OS-level C types (`pid_t`,
/// `c_char` buffers) from Rust.
fn main() -> io::Result<()> {
    // `libc::pid_t` is the OS-level C type for a process ID.
    let pid: libc::pid_t = unsafe { libc::getpid() };
    println!("pid: {pid}");

    // `libc::gethostname` fills a raw C char buffer, the same as it would in C.
    let mut buf = [0 as libc::c_char; 256];
    let ret = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if ret != 0 {
        return Err(io::Error::last_os_error());
    }
    let hostname = unsafe { CStr::from_ptr(buf.as_ptr()) };
    println!("hostname: {}", hostname.to_string_lossy());

    Ok(())
}
