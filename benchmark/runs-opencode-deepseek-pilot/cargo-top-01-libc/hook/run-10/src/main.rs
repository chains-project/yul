use std::ffi::CStr;

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    let gid: libc::gid_t = unsafe { libc::getgid() };

    println!("pid={pid} uid={uid} gid={gid}");

    let mut uts: libc::utsname = unsafe { std::mem::zeroed() };
    if unsafe { libc::uname(&mut uts) } == 0 {
        let sysname = unsafe { CStr::from_ptr(uts.sysname.as_ptr()) };
        let release = unsafe { CStr::from_ptr(uts.release.as_ptr()) };
        let machine = unsafe { CStr::from_ptr(uts.machine.as_ptr()) };
        println!(
            "{} {} {}",
            sysname.to_string_lossy(),
            release.to_string_lossy(),
            machine.to_string_lossy()
        );
    }
}
