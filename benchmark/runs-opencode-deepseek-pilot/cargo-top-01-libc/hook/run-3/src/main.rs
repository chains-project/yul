use std::ffi::CStr;
use std::io;

fn main() -> io::Result<()> {
    // SAFETY: getpid/getuid/getgid take no arguments and cannot fail.
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    let gid: libc::gid_t = unsafe { libc::getgid() };

    println!("pid={pid} uid={uid} gid={gid}");

    let mut uts: libc::utsname = unsafe { std::mem::zeroed() };
    // SAFETY: `uts` is a valid, zeroed utsname buffer for uname to populate.
    let ret = unsafe { libc::uname(&mut uts) };
    if ret != 0 {
        return Err(io::Error::last_os_error());
    }

    // SAFETY: uname() null-terminates sysname/release on success.
    let sysname = unsafe { CStr::from_ptr(uts.sysname.as_ptr()) };
    let release = unsafe { CStr::from_ptr(uts.release.as_ptr()) };
    println!(
        "sysname={} release={}",
        sysname.to_string_lossy(),
        release.to_string_lossy()
    );

    Ok(())
}
