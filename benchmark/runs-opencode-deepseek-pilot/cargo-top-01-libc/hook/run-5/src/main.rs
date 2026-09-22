use std::ffi::CStr;

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    println!("pid = {pid}");

    let mut uts: libc::utsname = unsafe { std::mem::zeroed() };
    if unsafe { libc::uname(&mut uts) } == 0 {
        let sysname = unsafe { CStr::from_ptr(uts.sysname.as_ptr()) };
        let release = unsafe { CStr::from_ptr(uts.release.as_ptr()) };
        println!(
            "{} {}",
            sysname.to_string_lossy(),
            release.to_string_lossy()
        );
    }
}
