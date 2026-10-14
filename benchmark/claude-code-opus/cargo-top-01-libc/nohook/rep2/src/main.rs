use std::ffi::CStr;
use std::io;
use std::mem::MaybeUninit;

/// Returns the system's node name and kernel release via `uname(2)`.
fn uname() -> io::Result<(String, String)> {
    let mut buf = MaybeUninit::<libc::utsname>::uninit();
    // SAFETY: `buf` is a valid, writable `utsname`; uname fills it on success.
    if unsafe { libc::uname(buf.as_mut_ptr()) } != 0 {
        return Err(io::Error::last_os_error());
    }
    // SAFETY: uname returned 0, so the struct is fully initialized.
    let buf = unsafe { buf.assume_init() };
    // SAFETY: the kernel guarantees these fields are NUL-terminated.
    let field = |f: &[libc::c_char]| unsafe { CStr::from_ptr(f.as_ptr()) }
        .to_string_lossy()
        .into_owned();
    Ok((field(&buf.nodename), field(&buf.release)))
}

fn main() -> io::Result<()> {
    // SAFETY: getpid/getuid have no preconditions and cannot fail.
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    let (host, release) = uname()?;

    println!("pid={pid} uid={uid} host={host} kernel={release}");
    Ok(())
}
