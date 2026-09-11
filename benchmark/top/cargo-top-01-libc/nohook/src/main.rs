use std::io;

/// Fetches the current process ID and hostname via raw libc calls,
/// demonstrating direct use of OS-level C types (`libc::pid_t`, `libc::c_char`).
fn main() -> io::Result<()> {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    println!("pid: {pid}");

    let mut buf = [0 as libc::c_char; 256];
    let ret = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if ret != 0 {
        return Err(io::Error::last_os_error());
    }

    let hostname = unsafe { std::ffi::CStr::from_ptr(buf.as_ptr()) };
    println!("hostname: {}", hostname.to_string_lossy());

    Ok(())
}
