use std::ffi::CStr;
use std::mem::MaybeUninit;

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    println!("pid: {pid}");

    let mut uts: MaybeUninit<libc::utsname> = MaybeUninit::uninit();
    let ret = unsafe { libc::uname(uts.as_mut_ptr()) };
    if ret == 0 {
        let uts = unsafe { uts.assume_init() };
        let sysname = unsafe { CStr::from_ptr(uts.sysname.as_ptr()) };
        println!("sysname: {}", sysname.to_string_lossy());
    }
}
