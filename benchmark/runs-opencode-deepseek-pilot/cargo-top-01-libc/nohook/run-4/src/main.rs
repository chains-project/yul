use std::ffi::CStr;
use std::io;

unsafe extern "C" {
    fn strlen(s: *const libc::c_char) -> libc::size_t;
}

fn main() -> io::Result<()> {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    let gid: libc::gid_t = unsafe { libc::getgid() };

    println!("pid={pid} uid={uid} gid={gid}");

    let mut uts: libc::utsname = unsafe { std::mem::zeroed() };
    let rc: libc::c_int = unsafe { libc::uname(&mut uts) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }

    let sysname = unsafe { CStr::from_ptr(uts.sysname.as_ptr()) };
    let release = unsafe { CStr::from_ptr(uts.release.as_ptr()) };
    let machine = unsafe { CStr::from_ptr(uts.machine.as_ptr()) };
    println!(
        "{} {} {}",
        sysname.to_string_lossy(),
        release.to_string_lossy(),
        machine.to_string_lossy()
    );

    let msg = c"sys-tool";
    let len: libc::size_t = unsafe { strlen(msg.as_ptr()) };
    println!("strlen={len}");

    Ok(())
}
